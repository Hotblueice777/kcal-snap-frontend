# streamlit_client\assistant_page.py

import os
import streamlit as st
import requests, base64, numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
import time

def render():
    BACKEND = os.getenv("BACKEND_URL")
    st.markdown("<h1 style='color:#766A8F;'>AI Health Assistant</h1>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # Azure speach
    with col1:
        if st.button("🎤 Speak Now"):
            import sounddevice as sd
            from scipy.io.wavfile import write

            fs = 44100
            seconds = 5
            st.info("Recording for 10 seconds...")
            myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
            sd.wait()
            write("input.wav", fs, myrecording)
            st.success("Recording complete!")

            # Step1: Speech → Text
            files = {"audio_file": open("input.wav", "rb")}
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
