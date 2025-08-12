# bruce_chat_app.py
import streamlit as st
from pathlib import Path
from huggingface_hub import InferenceClient

# ---------- إعداد الصفحة ----------
st.set_page_config(page_title="بروس 😄", page_icon="😄", layout="centered")

# (اختياري) شعار لو حبيت تحطه داخل assets/logo.png
logo_path = Path("assets/logo.png")
if logo_path.exists():
    st.image(str(logo_path), width=120)

st.title("بروس 😄")
st.caption("MVP — محادثة عربية بسيطة تعمل عبر Hugging Face Inference")

# ---------- التحقق من التوكن ----------
if "HF_TOKEN" not in st.secrets or not st.secrets["HF_TOKEN"]:
    st.error(
        "ما لقيت متغير HF_TOKEN في Secrets.\n"
        "روح لـ Manage app ▸ Settings ▸ Secrets وحط:\n\nHF_TOKEN = \"hf_...\""
    )
    st.stop()
MODEL_ID = "HuggingFaceH4/zephyr-7b-beta"
HF_TOKEN = st.secrets["HF_TOKEN"]

# ---------- إعداد العميل والموديل ----------
# تقدر تغيّر الموديل لأي موديل يدعم text-generation على Hugging Face

client = InferenceClient(model=MODEL_ID, token=HF_TOKEN)

# ---------- ذاكرة المحادثة ----------
if "history" not in st.session_state:
    st.session_state.history = []  # عناصر بشكل: [("user", "..."), ("assistant", "...")]

SYSTEM_PROMPT = (
    "أنت بروس، رد بالعربية بشكل واضح ولطيف ومختصر.\n"
    "إذا سأل المستخدم عن خطوات تقنية، اعطه خطوات مرقمة وبسيطة.\n"
    "تجنب الردود الطويلة جداً."
)

def build_prompt(history: list[tuple[str, str]], user_text: str) -> str:
    """
    نبني برومبت بسيط للموديلات اللي تشتغل بنمط text-generation (مو محادثة أصلية).
    """
    parts = [SYSTEM_PROMPT, ""]
    for role, content in history:
        if role == "user":
            parts.append(f"المستخدم: {content}")
        else:
            parts.append(f"بروس: {content}")
    parts.append(f"المستخدم: {user_text}")
    parts.append("بروس:")
    return "\n".join(parts)

def generate_response(history: list[tuple[str, str]], user_text: str) -> str:
    prompt = build_prompt(history, user_text)
    # نطلب نص جديد فقط (بدون إعادة النص الأصلي)
    # ملاحظة: بعض الموديلات تتعامل أفضل مع do_sample=True وبعضها False؛ جرّب لو حبيت
    out = client.text_generation(
        prompt,
        max_new_tokens=256,
        temperature=0.2,
        top_p=0.9,
        repetition_penalty=1.1,
        do_sample=True,
        return_full_text=False,
    )
    # بعض السرفرات ترجع كائن/ديكت، وبعضها سترينغ—نضمن التحويل لنص
    return str(out).strip()

# ---------- الواجهة ----------
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("اكتب رسالتك...", placeholder="مثلاً: أهلاً بروس", label_visibility="collapsed")
    submitted = st.form_submit_button("إرسال")

# زر سريع للتجارب
if st.button("اهلا بروس", use_container_width=True):
    st.session_state.history.append(("user", "أهلًا بروس"))
    try:
        reply = generate_response(st.session_state.history, "أهلًا بروس")
    except Exception as e:
        st.error(f"صار خطأ أثناء الاتصال بالخدمة:\n\n{e}")
    else:
        st.session_state.history.append(("assistant", reply))
        st.rerun()

# عرض الرسائل السابقة
for role, content in st.session_state.history:
    if role == "user":
        st.chat_message("user").markdown(content)
    else:
        st.chat_message("assistant").markdown(content)

# معالجة الإرسال من الحقل
if submitted and user_input.strip():
    st.chat_message("user").markdown(user_input)
    st.session_state.history.append(("user", user_input))
    try:
        reply = generate_response(st.session_state.history, user_input)
    except Exception as e:
        st.error(
            "صار خطأ أثناء الاتصال بالخدمة.\n\n"
            f"{e}\n\n"
            "إذا شفت رسالة فيها 'not supported for task text-generation' غيّر MODEL_ID لموديل يدعم text-generation."
        )
    else:
        st.session_state.history.append(("assistant", reply))
        st.chat_message("assistant").markdown(reply)

# أدوات جانبية
with st.sidebar:
    st.header("إعدادات")
    st.write(f"الموديل الحالي: `{MODEL_ID}`")
    if st.button("مسح المحادثة"):
        st.session_state.history = []
        st.experimental_rerun()
