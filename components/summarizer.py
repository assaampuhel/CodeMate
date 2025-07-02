

import streamlit as st
from ai.summarizer import summarize_text

def show_summarizer():
    st.title("📝 Notes Summarizer")
    st.markdown("Upload or paste notes, and get a concise summary powered by AI.")

    mode = st.radio("Choose Input Method", ["Paste Text", "Upload File"])

    user_input = ""
    if mode == "Paste Text":
        user_input = st.text_area("Enter your notes here:", height=300)
    else:
        uploaded_file = st.file_uploader("Upload a .txt file", type=["txt"])
        if uploaded_file is not None:
            user_input = uploaded_file.read().decode("utf-8")
            st.text_area("File Content", user_input, height=300)

    model_choice = st.selectbox("Select Summarization Model", ["OpenAI GPT-3.5", "HuggingFace T5-Small"])

    if st.button("Summarize"):
        if user_input.strip():
            with st.spinner("Generating summary..."):
                summary = summarize_text(user_input, model=model_choice)
            st.subheader("🔍 Summary:")
            st.success(summary)
        else:
            st.warning("Please provide some input to summarize.")