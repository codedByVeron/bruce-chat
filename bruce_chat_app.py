# Bruce Chat — Streamlit + OpenAI
import os
from pathlib import Path
import streamlit as st
from openai import OpenAI

# إعدادات الصفحة
st.set_page_config(page_title="بروس 😎", page_icon="🤖", layout="centered")

# لوغو (اختياري)
logo_path = Path("assets/logo.png")
if logo_path.exists():
    st.image(str(logo_path), width=120)
st.title("بروس")
st.caption("MVP — يرد بالعربي بشكل واضح وسريع.")

# تهيئة العميل + التحقق من السر
def get_client():
    if not os.environ.get("OPENAI_API_KEY"):
        st.error("ما لقيت السر OPENAI_API_KEY.\nاذهب إلى: App → Settings → Secrets وأضفه هناك.")
        st.stop()
    return OpenAI()
client = get_client()

# المولّد
def generate(history, user_msg):
    system = (
        "أنت مساعد اسمه بروس. ردّ بالعربية الواضحة، مختصر وبدون تكرار. "
        "إذا كان الطلب غامض، اسأل سؤال توضيحي قصير. لا تستخدم لهجة جارفيز 😂."
    )
    msgs = [{"role": "system", "content": system}]
    for u, a in history[-8:]:
        msgs.append({"role": "user", "content": u})
        msgs.append({"role": "assistant", "content": a})
    msgs.append({"role": "user", "content": user_msg})

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=msgs,
        temperature=0.6,
        max_tokens=350,
    )
    return resp.choices[0].message.content.strip()

# حالة المحادثة + الواجهة
if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    if st.button("مسح المحادثة"):
        st.session_state.history.clear()
        st.rerun()

# عرض المحادثة السابقة
for u, a in st.session_state.history:
    with st.chat_message("user"):
        st.markdown(u)
    with st.chat_message("assistant"):
        st.markdown(a)

# إدخال المستخدم
prompt = st.chat_input("اكتب رسالتك…")
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.spinner("بروس يكتب…"):
        reply = generate(st.session_state.history, prompt)
    st.session_state.history.append((prompt, reply))
    with st.chat_message("assistant"):
        st.markdown(reply)
