# bruce_chat_app.py
import streamlit as st
from huggingface_hub import InferenceClient
import os

# ===== إعداد الصفحة =====
st.set_page_config(page_title="بروس 😁", page_icon="😁", layout="centered")
st.title("بروس 😁")
st.caption("MVP — محادثة عربية بسيطة تعمل عبر Hugging Face Inference")

# ===== التحقق من التوكن =====
HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    st.error("مفقود HF_TOKEN في Secrets. روح إلى Manage app → Settings → Secrets وحط:\nHF_TOKEN = \"hf_...\"")
    st.stop()

# اختر أحد الموديلات الداعمة للمحادثة (chat)
MODEL_ID = st.sidebar.selectbox(
    "الموديل الحالي:",
    [
        "HuggingFaceH4/zephyr-7b-beta",
        "mistralai/Mistral-7B-Instruct-v0.2",
        "tiiuae/falcon-7b-instruct",  # لو ما اشتغل ارجع لواحد من فوق
    ],
    index=0,
)

SYSTEM_PROMPT = (
    "أنت روبوت دردشة اسمه بروس. رد بالعربية بشكل ودود، واضح ومختصر. "
    "استخدم جمل قصيرة، واذا ما تقدر تساعد، قل ذلك بصراحة."
)

# ===== تهيئة العميل =====
client = InferenceClient(api_key=HF_TOKEN)

# ===== دوال الموديل (صيغة محادثة) =====
def generate_reply(history: list[tuple[str, str]], user_msg: str) -> str:
    """
    history: قائمة من tuples [(role, content), ...] مثل:
             [("user","..."), ("assistant","..."), ...]
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    # أضف المحادثة السابقة
    for role, content in history:
        role = "assistant" if role == "assistant" else "user"
        messages.append({"role": role, "content": content})
    # أضف رسالة المستخدم الحالية
    messages.append({"role": "user", "content": user_msg})

    # استدعاء chat.completions (مو text-generation)
    resp = client.chat.completions.create(
        model=MODEL_ID,
        messages=messages,
        max_tokens=350,
        temperature=0.7,
    )
    return resp.choices[0].message.content.strip()

# ===== واجهة Streamlit =====
if "history" not in st.session_state:
    st.session_state.history = []  # [(role, content)]

with st.form("chat_form", clear_on_submit=True):
    user_text = st.text_input("مثلاً: أهلًا بروس!", placeholder="اكتب رسالتك...", label_visibility="collapsed")
    submitted = st.form_submit_button("إرسال")

if submitted and user_text.strip():
    with st.spinner("يكتب…"):
        try:
            reply = generate_reply(st.session_state.history, user_text.strip())
        except Exception as e:
            st.error(f"صار خطأ أثناء الاتصال بالخدمة:\n\n{e}\n\n"
                     "لو شفت رسالة 'not supported for task text-generation' تأكد إننا نستخدم chat "
                     "وجرب موديل آخر من الشريط الجانبي.")
        else:
            st.session_state.history.append(("user", user_text.strip()))
            st.session_state.history.append(("assistant", reply))

# طباعة المحادثة
for role, msg in st.session_state.history:
    if role == "user":
        st.chat_message("user").markdown(msg)
    else:
        st.chat_message("assistant").markdown(msg)

# زر لمسح المحادثة
st.sidebar.subheader("إعدادات")
if st.sidebar.button("مسح المحادثة"):
    st.session_state.history = []
    st.experimental_rerun()
