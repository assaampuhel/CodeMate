import streamlit as st
from ai.flashcard_gen import generate_flashcards

def show_flashcards():
    st.set_page_config(layout="wide")
    st.title("📇 AI Flashcard Generator")
    st.markdown("Convert your programming notes or definitions into interactive flashcards.")

    col1, col2 = st.columns([2, 1])
    with col1:
        notes = st.text_area("Paste notes, concepts, or explanations below:", height=300, placeholder="e.g. Functions are reusable blocks of code...")

    with col2:
        model_choice = st.selectbox("Summarization Model", ["OpenAI GPT-3.5", "HuggingFace T5-Small"])

    if st.button("Generate Flashcards"):
        if notes.strip():
            with st.spinner("Generating flashcards..."):
                flashcards = generate_flashcards(notes, model=model_choice)

            if flashcards:
                st.success(f"Generated {len(flashcards)} flashcards!")
                for i, card in enumerate(flashcards, 1):
                    with st.expander(f"Flashcard {i}", expanded=False):
                        st.markdown(f"**Q:** {card['question']}")
                        st.markdown(f"**A:** {card['answer']}")
            else:
                st.error("No flashcards were generated. Please try a different input.")
        else:
            st.warning("Please provide some content to create flashcards.")
