# -*- coding: utf-8 -*-
import streamlit as st
from huggingface_hub import InferenceClient

# -----------------------------
# إعدادات عامة
# -----------------------------
st.set_page_config(page_title="بــروس 😄", page_icon="🤖", layout="centered")

# اقرأ مفتاح Hugging Face من السيكرتس
if "HF_API_KEY" not in st.secrets:
    st.error('مفتاح Hugging Face مفقود. ادخل على Manage app → Settings → Secrets وحط:\nHF_API_KEY = "hf_..."')
    st.stop()

HF_KEY = st.secrets["HF_API_KEY"]

# اختَر موديل متاح على Inference API (لا يحتاج موافقة خاصة)
# لو واجهت بطء جرّب تبدل للموديل الثاني
MODEL_ID = "google/gemma-2-2b-it"  # خيار خفيف
# MODEL_ID = "HuggingFaceH4/zephyr-7b-beta"  # بديل

client = InferenceClient(api_key=HF_KEY)

SYSTEM_PROMPT = (
    "انتَ بروس، ردّ بأسلوب عربي بسيط، لطيف، ومباشر. "
    "اختصر قدر الإمكان، واذا طلب المستخدم خطوات فاعطِها مرقّمة. "
    "لا تذكر سياسات أو مفاتيح أو إعدادات داخلية."
)

# -----------------------------
# دوال المساعد
# -----------------------------
def chat_via_hf(messages, max_tokens=350, temperature=0.7):
    """
    نحاول أولاً chat_completion (لو متاحة في نسختك من huggingface_hub)،
    ولو فشلت نرجع لطريقة text_generation مع قالب محادثة بسيط.
    """
    # 1) تجربة chat_completion (قد لا تتوفر في اصدارات قديمة)
    try:
        resp = client.chat_completion(
            model=MODEL_ID,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        # استرجاع النص
        return resp.choices[0].message.content.strip()
    except Exception:
        pass

    # 2)Fallback: text_generation مع قالب محادثة
    # نحول الرسائل إلى برومبت واحد
    prompt_lines = [f"system: {SYSTEM_PROMPT}"]
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        prompt_lines.append(f"{role}: {content}")
    prompt_lines.append("assistant:")

    prompt = "\n".join(prompt_lines)

    out = client.text_generation(
        model=MODEL_ID,
        prompt=prompt,
        temperature=temperature,
        max_new_tokens=max_tokens,
        do_sample=True,
        return_full_text=False,
    )
    # بعض الإصدارات ترجع string مباشرة
    if isinstance(out, str):
        return out.strip()
    # وبعضها dict/obj فيه "generated_text"
    gen = getattr(out, "generated_text", None) or out.get("generated_text", "")
    return (gen or "").strip()


def generate_response(history, user_text):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += history
    messages.append({"role": "user", "content": user_text})
    return chat_via_hf(messages)


# -----------------------------
# واجهة Streamlit
# -----------------------------
st.title("بــروس 😄")
st.caption("MVP — محادثة عربية بسيطة (تعمل عبر Hugging Face Inference)")

# حالة المحادثة
if "history" not in st.session_state:
    st.session_state.history = []

# عرض السجل
for turn in st.session_state.history:
    if turn["role"] == "user":
        st.chat_message("user").markdown(turn["content"])
    else:
        st.chat_message("assistant").markdown(turn["content"])

# حقل الإدخال
user_msg = st.chat_input("اكتب رسالتك...")

if user_msg:
    # أضف رسالة المستخدم
    st.session_state.history.append({"role": "user", "content": user_msg})
    st.chat_message("user").markdown(user_msg)

    with st.spinner("⏳ يفكر..."):
        try:
            reply = generate_response(st.session_state.history, user_msg)
        except Exception as e:
            st.error(f"صار خطأ أثناء الاتصال بالخدمة: {e}")
            st.stop()

    # أضف رد المساعد
    st.session_state.history.append({"role": "assistant", "content": reply})
    st.chat_message("assistant").markdown(reply)

# شريط جانبي
with st.sidebar:
    st.header("إعدادات")
    if st.button("مسح المحادثة"):
        st.session_state.history = []
        st.experimental_rerun()

    st.caption(":bulb: تلميح: لو حسّيت بطء، جرّب تبدّل MODEL_ID في أعلى الملف إلى موديل آخر يدعم Inference API.")
