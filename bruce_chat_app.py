import streamlit as st
from openai import OpenAI

# تفعيل الـ API Key من الـ Secrets في Streamlit
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="بروس 😁", page_icon="😁")

if "history" not in st.session_state:
    st.session_state.history = []

st.title("بروس 😁")
st.caption("MVP — يرد بالعربي بشكل واضح وسريع")

# دالة لتوليد الردود من OpenAI
def generate(history, user_input):
    messages = [{"role": "system", "content": "أنت بروس، رد بالعربية بشكل واضح ومختصر."}]
    for u, a in history:
        messages.append({"role": "user", "content": u})
        messages.append({"role": "assistant", "content": a})
    messages.append({"role": "user", "content": user_input})

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=350
    )
    reply = resp.choices[0].message.content
    return reply

# عرض المحادثة السابقة
for user_msg, bot_msg in st.session_state.history:
    with st.chat_message("user"):
        st.markdown(user_msg)
    with st.chat_message("assistant"):
        st.markdown(bot_msg)

# إدخال المستخدم
if prompt := st.chat_input("...اكتب رسالتك"):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("⏳ بروس يكتب..."):
            reply = generate(st.session_state.history, prompt)
            st.session_state.history.append((prompt, reply))
            st.markdown(reply)
