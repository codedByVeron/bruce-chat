import streamlit as st
import requests
import os

# إعداد الصفحة
st.set_page_config(page_title="بروس 😁", layout="centered")

st.title("بروس 😁")
st.write("MVP — محادثة عربية بسيطة تعمل عبر Hugging Face Inference")

# قراءة التوكن من Secrets
HF_TOKEN = os.getenv("HF_TOKEN")

# اختيار الموديل
MODEL_ID = st.sidebar.selectbox(
    "الموديل الحالي:",
    [
        "HuggingFaceH4/zephyr-7b-beta",
        "tiiuae/falcon-7b-instruct",
        "mistralai/Mistral-7B-Instruct-v0.2"
    ]
)

# دالة إرسال الرسالة لـ Hugging Face
def query_huggingface(prompt):
    API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": prompt}
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and "generated_text" in data[0]:
                return data[0]["generated_text"]
            elif isinstance(data, dict) and "generated_text" in data:
                return data["generated_text"]
        return f"⚠️ خطأ من API: {response.text}"
    except Exception as e:
        return f"⚠️ استثناء: {e}"

# حفظ المحادثة
if "history" not in st.session_state:
    st.session_state.history = []

# مربع إدخال المستخدم
user_msg = st.text_input("...اكتب رسالتك")

# زر الإرسال
if st.button("إرسال"):
    if user_msg.strip():
        st.session_state.history.append(("أنت", user_msg))
        bot_reply = query_huggingface(user_msg)
        st.session_state.history.append(("بروس", bot_reply))
        st.rerun()

# عرض المحادثة
for sender, message in st.session_state.history:
    if sender == "أنت":
        st.markdown(f"**🧑‍💻 {sender}:** {message}")
    else:
        st.markdown(f"**🤖 {sender}:** {message}")

# زر مسح المحادثة
if st.sidebar.button("مسح المحادثة"):
    st.session_state.history = []
    st.rerun()
