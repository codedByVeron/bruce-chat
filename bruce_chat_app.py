import os
import time
import json
import requests
import streamlit as st

# ---------- إعداد الصفحة ----------
st.set_page_config(page_title="بروس 😊", page_icon="🙂", layout="centered")
st.title("بروس 😊")
st.write("MVP — محادثة عربية بسيطة تعمل عبر Hugging Face Inference")

# ---------- سرّ Hugging Face ----------
HF_TOKEN = os.getenv("HF_TOKEN")

with st.expander("إعدادات"):
    st.caption("الموديل الحالي:")
    # اختر موديل معروف مدعوم للتوليد
    MODEL_ID = st.selectbox(
        "اختر موديلًا",
        [
            "mistralai/Mistral-7B-Instruct-v0.2",
            "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        ],
        index=0,
        label_visibility="collapsed",
    )
    if st.button("مسح المحادثة"):
        st.session_state.history = []

# ---------- فحص التوكن ----------
if not HF_TOKEN:
    st.error("⚠️ ما حصلت HF_TOKEN. روّح إلى Manage app → Settings → Secrets وحط:\nHF_TOKEN = \"hf_xxxxxxxxx\"")
    st.stop()

# ---------- تهيئة الحالة ----------
if "history" not in st.session_state:
    st.session_state.history = []

# ---------- دالة الطلب ----------
HF_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

def call_hf(messages, max_new_tokens=128):
    """
    يحاول يرسل المحادثة كمطالبة نصية بسيطة (أكثر توافقاً).
    """
    # نحول التاريخ لنص واحد: system + user/assistant
    system = "أنت روبوت دردشة عربي ولطيف ودقيق."
    parts = [f"system: {system}"]
    for role, text in messages:
        parts.append(f"{role}: {text}")
    parts.append("assistant:")

    payload = {
        "inputs": "\n".join(parts),
        "parameters": {
            "max_new_tokens": max_new_tokens,
            "temperature": 0.7,
            "return_full_text": False,
        }
    }

    # جرّب عدة مرات لو السيرفر يحمّل الموديل (503)
    for _ in range(6):
        resp = requests.post(HF_URL, headers=HEADERS, json=payload, timeout=60)
        if resp.status_code == 200:
            try:
                data = resp.json()
                if isinstance(data, list) and data and "generated_text" in data[0]:
                    return data[0]["generated_text"].strip()
                # بعض المزودين يرجعون dict
                if isinstance(data, dict) and "generated_text" in data:
                    return data["generated_text"].strip()
                return json.dumps(data)  # لو صيغة مختلفة، نعرضها
            except Exception as e:
                return f"[Parsing error] {e}"
        elif resp.status_code == 503:
            # الموديل لسه يشتغل - انتظر شوية
            time.sleep(2)
            continue
        else:
            try:
                err = resp.json()
            except Exception:
                err = resp.text
            return f"API error ({resp.status_code}): {err}"

    return "الخدمة مشغولة الآن (503 متكرر). جرّب بعد لحظات."

# ---------- واجهة الإدخال ----------
user_msg = st.text_input("اكتب رسالتك...", placeholder="مثلاً: أهلاً بروس!")
send = st.button("إرسال")

if send and user_msg.strip():
    st.session_state.history.append(("user", user_msg.strip()))
    with st.spinner("يرد بروس…"):
        reply = call_hf(st.session_state.history, max_new_tokens=160)
    st.session_state.history.append(("assistant", reply))

# ---------- عرض المحادثة ----------
for role, text in st.session_state.history:
    if role == "user":
        st.chat_message("user").markdown(text)
    else:
        st.chat_message("assistant").markdown(text)
