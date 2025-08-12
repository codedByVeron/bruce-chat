
# Bruce Chat – Streamlit
import streamlit as st
from transformers import pipeline
from pathlib import Path

st.set_page_config(page_title="Bruce Chat", page_icon="🤖", layout="centered")

# لوغو (اختياري)
logo_path = Path("assets/logo.png")
if logo_path.exists():
    st.image(str(logo_path), width=120)
st.title("بــروس 🤖")
st.caption("MVP محادثة – لاحقًا نربطه بالصوت والروبوت")

@st.cache_resource(show_spinner=False)
def load_model():
    # نموذج خفيف يشتغل على CPU
    return pipeline("text-generation", model="distilgpt2", max_new_tokens=180)

gen = load_model()

def build_prompt(history, user):
    persona = ("أنت روبوت اسمه بروس. ترد بالعربية بشكل مختصر، لطيف، وواضح. "
               "إذا الطلب غامض، اسأل سؤال توضيحي قصير.")
    hist = "\n".join([f"المستخدم: {u}\nبروس: {a}" for u, a in history[-8:]])
    return f"{persona}\n\n{hist}\nالمستخدم: {user}\nبروس:"

def generate(history, user):
    out = gen(build_prompt(history, user), do_sample=True, temperature=0.8, top_p=0.95)[0]["generated_text"]
    ans = out.split("بروس:", 1)[-1].strip()
    return ans.replace("المستخدم:", "").split("\n")[0].strip()

if "chat" not in st.session_state:
    st.session_state.chat = []

with st.sidebar:
    st.subheader("إعدادات")
    if st.button("مسح المحادثة"):
        st.session_state.chat = []
        st.rerun()

# عرض المحادثة
for u, a in st.session_state.chat:
    with st.chat_message("user"):
        st.write(u)
    with st.chat_message("assistant"):
        st.write(a)

# إدخال
msg = st.chat_input("اكتب رسالتك…")
if msg:
    with st.chat_message("user"):
        st.write(msg)
    with st.chat_message("assistant"):
        with st.spinner("بروس يفكّر…"):
            ans = generate(st.session_state.chat, msg) or "تمام، وضّح أكثر؟"
            st.write(ans)
    st.session_state.chat.append((msg, ans))
