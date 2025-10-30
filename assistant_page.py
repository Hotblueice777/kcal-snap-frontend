# streamlit_client\assistant_page.py

import os
import streamlit as st
import requests, base64
from io import BytesIO  
import time

def render():
    BACKEND = os.getenv("BACKEND_URL")
    st.markdown("<h1 style='color:#766A8F;'>AI Health Assistant</h1>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # Azure speach
    with col1:
        audio_data = st.audio_input("🎤 Record or upload your voice")  # Streamlit 1.36+ 

        if audio_data is not None:
            st.info("Processing your recording...")

            # Step1: Speech → Text
            files = {"audio_file": audio_data}
            r = requests.post(f"{BACKEND}/assistant/api/speech_to_text", files=files)
            text = r.json().get("text", "")
            if not text:
                st.warning("Speech not recognized.")
                return
            st.write(f"🗣 You said: {text}")

            # Step2: Text → RAG
            with st.spinner("Thinking..."):
                r2 = requests.post(f"{BACKEND}/assistant/api/ask_rag", json={"text": text})
                answer = r2.json().get("answer", "No response.")
                st.success(answer)

            # Step3: RAG Answer → Speech
            with st.spinner("Converting to speech..."):
                tts = requests.post(f"{BACKEND}/assistant/api/text_to_speech", json={"text": answer})
                audio_base64 = tts.json().get("audio", "")
                if audio_base64:
                    st.audio(base64.b64decode(audio_base64), format="audio/wav")

    # QnA text
    with col2:
        user_input = st.text_input("💬 Type your question")
        if st.button("Ask Assistant"):
            with st.spinner("Thinking..."):
                r = requests.post(f"{BACKEND}/assistant/api/ask_rag", json={"text": user_input})
                answer = r.json().get("answer", "No response.")
                st.success(answer)
