import streamlit as st
from openai import OpenAI

# إنشاء عميل OpenAI
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# عنوان التطبيق
st.set_page_config(page_title="بروس", page_icon="🤖")
st.title("🤖 بروس")

# حفظ المحادثة في الجلسة
if "history" not in st.session_state:
    st.session_state.history = []

# دالة توليد الرد
def generate_response(history, prompt):
    messages = [{"role": "system", "content": "أنت بروس، روبوت ذكي يتكلم باللهجة العربية بطابع ودود."}]
    for h in history:
        messages.append({"role": "user", "content": h[0]})
        messages.append({"role": "assistant", "content": h[1]})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=350
    )

    return response.choices[0].message.content

# إدخال المستخدم
prompt = st.chat_input("💬 اكتب رسالتك هنا...")

if prompt:
    with st.spinner("🤖 بروس يكتب الرد..."):
        reply = generate_response(st.session_state.history, prompt)
        st.session_state.history.append((prompt, reply))

# عرض المحادثة
for user_msg, bot_reply in st.session_state.history:
    st.chat_message("user").markdown(user_msg)
    st.chat_message("assistant").markdown(bot_reply)
