# bruce_chat_app.py

import streamlit as st
from openai import OpenAI

# إعداد الصفحة
st.set_page_config(page_title="بروس", page_icon="🤖", layout="centered")
st.title("🤖 بروس")
st.caption("MVP — محادثة عربية بسيطة (يتطلب مفتاح OpenAI في Secrets)")

# التحقق من وجود المفتاح
if "OPENAI_API_KEY" not in st.secrets or not st.secrets["OPENAI_API_KEY"]:
    st.error("⚠️ ما لقيت OPENAI_API_KEY في Secrets.\nاذهب إلى: Manage app → Settings → Secrets وأضف:\n\nOPENAI_API_KEY = \"sk-...\"")
    st.stop()

# عميل OpenAI
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# حالة المحادثة
if "history" not in st.session_state:
    st.session_state.history = []  # عناصرها [(user, assistant), ...]

SYSTEM_PROMPT = (
    "أنت بروس: مساعد عربي ودود، مختصر وواضح، ترد باللهجة السهلة."
    " إذا كان الطلب غامض اطلب توضيح. استخدم فقرات قصيرة وقوائم عند الحاجة."
)

def generate_response(history: list[tuple[str, str]], user_msg: str) -> str:
    """ينشئ رسالة للـ API من التاريخ ويرجع رد المساعد."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for u, a in history:
        messages.append({"role": "user", "content": u})
        messages.append({"role": "assistant", "content": a})
    messages.append({"role": "user", "content": user_msg})

    # استدعاء Chat Completions (الواجهة المستقرة في بايثون 1.x)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=350,
        temperature=0.6,
    )
    return resp.choices[0].message.content.strip()

# واجهة الدردشة
with st.sidebar:
    if st.button("مسح المحادثة", use_container_width=True):
        st.session_state.history = []
        st.experimental_rerun()

# عرض المحادثات السابقة
for u, a in st.session_state.history:
    st.chat_message("user").markdown(u)
    st.chat_message("assistant").markdown(a)

# إدخال المستخدم
user_input = st.chat_input("اكتب رسالتك هنا…")
if user_input:
    st.chat_message("user").markdown(user_input)
    with st.spinner("🤖 بروس يكتب الرد…"):
        try:
            reply = generate_response(st.session_state.history, user_input)
        except Exception as e:
            st.error(f"صار خطأ أثناء الاتصال بـ OpenAI:\n\n{e}")
        else:
            st.session_state.history.append((user_input, reply))
            st.chat_message("assistant").markdown(reply)
