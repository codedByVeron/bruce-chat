# bruce_chat_app.py

import streamlit as st
from pathlib import Path
from huggingface_hub import InferenceClient

# إعداد الصفحة
st.set_page_config(page_title="بروس 😄", page_icon="😄", layout="centered")

# (اختياري) شعار
logo_path = Path("assets/logo.png")
if logo_path.exists():
    st.image(str(logo_path), width=120)

st.title("بروس 😄")
st.caption("MVP — محادثة عربية بسيطة (تعمل عبر Hugging Face Inference)")

# التحقق من وجود التوكن
if "HF_TOKEN" not in st.secrets or not st.secrets["HF_TOKEN"]:
    st.error("🔑 ما لقيت HF_TOKEN في Secrets. روح لـ Manage app → Settings → Secrets وحطه هناك.")
    st.stop()

# عميل Hugging Face
MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.3"  # موديل يدعم text-generation
client = InferenceClient(model=MODEL_ID, token=st.secrets["HF_TOKEN"])

# ذاكرة الدردشة
if "history" not in st.session_state:
    st.session_state.history = []  # [(user, assistant), ...]

SYSTEM_PROMPT = (
    "أنت بروس، رد بالعربية بشكل واضح ولطيف، وخلّك مختصر ومفيد. "
    "إذا سأل المستخدم عن الوقت أو شيء عام، جاوبه ببساطة. "
    "تجنّب الكلام الطويل إلا لو طلب صراحة."
)

def build_prompt(history, user_message):
    """
    نبني prompt بأسلوب [INST] للنماذج التعليمية مثل Mistral-Instruct.
    """
    parts = [f"<s>[INST] {SYSTEM_PROMPT} [/INST]"]
    for u, a in history:
        parts.append(f"{a}</s><s>[INST] {u} [/INST]")
    parts.append("")  # يفصل آخر رد
    parts.append(f"[/INST]")  # إغلاق لو في سطر سابق
    # آخر رسالة من المستخدم
    prompt = "<s>[INST] " + user_message + " [/INST]"
    full = "\n".join(parts) + "\n" + prompt
    return full

def generate_response(history, user_message):
    prompt = build_prompt(history, user_message)
    # توليد نص
    out = client.text_generation(
        prompt,
        max_new_tokens=200,
        temperature=0.7,
        top_p=0.9,
        do_sample=True,
        repetition_penalty=1.1,
        stop=["</s>", "[INST]", "[/INST]"],  # يحاول يوقف بشكل نظيف
        return_full_text=False,              # رجّع الناتج فقط بدون البرومبت
    )
    # `out` يكون سترنغ الناتج
    return out.strip()

# واجهة بسيطة
with st.form("chat"):
    user = st.text_input("اكتب رسالتك…", "")
    sent = st.form_submit_button("إرسال", use_container_width=True)

# عرض التاريخ
for u, a in st.session_state.history:
    st.chat_message("user").markdown(u)
    st.chat_message("assistant").markdown(a)

if sent and user.strip():
    st.chat_message("user").markdown(user)
    with st.spinner("⏳ بروس يفكر…"):
        try:
            reply = generate_response(st.session_state.history, user.strip())
        except Exception as e:
            st.error(f"صار خطأ أثناء الاتصال بالخدمة:\n\n{e}")
            st.stop()
    st.session_state.history.append((user.strip(), reply))
    st.chat_message("assistant").markdown(reply)

# زر مسح المحادثة
with st.sidebar:
    if st.button("مسح المحادثة"):
        st.session_state.history = []
        st.success("انمسحت السالفة ✅")
