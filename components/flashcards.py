import streamlit as st
from ai.flashcard_gen import generate_flashcards
import pandas as pd
import io

def show_flashcards():
    st.set_page_config(layout="wide")
    st.title("📇 AI Flashcard Generator")
    st.markdown("Convert your programming notes or definitions into interactive flashcards.")

    col1, col2 = st.columns([2, 1])
    with col1:
        notes = st.text_area("Paste notes, concepts, or explanations below:", height=300, placeholder="e.g. Functions are reusable blocks of code...")

    with col2:
        model_choice = st.selectbox("Summarization Model", ["OpenAI GPT-3.5", "HuggingFace T5-Small"])

    # Session state initialization for flashcards, index, show_answer
    if "flashcards_data" not in st.session_state:
        st.session_state.flashcards_data = []
    if "flashcard_index" not in st.session_state:
        st.session_state.flashcard_index = 0
    if "show_answer" not in st.session_state:
        st.session_state.show_answer = False

    if st.button("Generate Flashcards"):
        if notes.strip():
            with st.spinner("Generating flashcards..."):
                flashcards = generate_flashcards(notes, model=model_choice)
            if flashcards:
                st.session_state.flashcards_data = flashcards
                st.session_state.flashcard_index = 0
                st.session_state.show_answer = False
                st.success(f"Generated {len(flashcards)} flashcards!")
            else:
                st.error("No flashcards were generated. Please try a different input.")
        else:
            st.warning("Please provide some content to create flashcards.")

    # Flashcard import
    st.divider()
    st.markdown("### 📥 Import Flashcards")

    uploaded_file = st.file_uploader("Upload a CSV or TSV file", type=["csv", "txt", "tsv"])

    if uploaded_file:
        try:
            ext = uploaded_file.name.split('.')[-1]
            if ext == "csv":
                df = pd.read_csv(uploaded_file)
            elif ext in ["tsv", "txt"]:
                df = pd.read_csv(uploaded_file, sep="\t", header=None, names=["question", "answer"])
            else:
                st.warning("Unsupported file format.")

            if "question" in df.columns and "answer" in df.columns:
                st.session_state.flashcards_data = df.to_dict(orient="records")
                st.session_state.flashcard_index = 0
                st.session_state.show_answer = False
                st.success(f"Imported {len(st.session_state.flashcards_data)} flashcards successfully.")
            else:
                st.error("Invalid file structure. Please ensure it contains 'question' and 'answer' columns.")

        except Exception as e:
            st.error(f"Error processing file: {e}")

    # Show flashcards if present
    if st.session_state.flashcards_data:
        st.divider()
        mode = st.radio("Review Mode", ["List View", "Study One-by-One"], horizontal=True)

        if mode == "List View":
            for i, card in enumerate(st.session_state.flashcards_data):
                with st.expander(f"Flashcard {i + 1}", expanded=False):
                    q_key = f"question_{i}"
                    a_key = f"answer_{i}"

                    new_q = st.text_input("Question", value=card["question"], key=q_key)
                    new_a = st.text_area("Answer", value=card["answer"], height=100, key=a_key)

                    col_edit, col_delete = st.columns([1, 1])
                    with col_edit:
                        if st.button("Save", key=f"save_{i}"):
                            st.session_state.flashcards_data[i] = {"question": new_q, "answer": new_a}
                            st.success(f"Flashcard {i + 1} updated.")
                    with col_delete:
                        if st.button("Delete", key=f"delete_{i}"):
                            del st.session_state.flashcards_data[i]
                            st.success(f"Flashcard {i + 1} deleted.")
                            st.experimental_rerun()
        else:
            cards = st.session_state.flashcards_data
            index = st.session_state.flashcard_index
            total = len(cards)

            st.subheader(f"Flashcard {index + 1} of {total}")
            st.markdown(f"**Q:** {cards[index]['question']}")

            if not st.session_state.show_answer:
                if st.button("Show Answer"):
                    st.session_state.show_answer = True
            else:
                st.info(f"**A:** {cards[index]['answer']}")

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Previous") and index > 0:
                    st.session_state.flashcard_index -= 1
                    st.session_state.show_answer = False
            with col2:
                if st.button("Restart"):
                    st.session_state.flashcard_index = 0
                    st.session_state.show_answer = False
            with col3:
                if st.button("Next") and index < total - 1:
                    st.session_state.flashcard_index += 1
                    st.session_state.show_answer = False

    if st.session_state.flashcards_data:
        st.divider()
        st.markdown("### 📤 Export Flashcards")

        # Convert flashcards to DataFrame
        df = pd.DataFrame(st.session_state.flashcards_data)

        # CSV export
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📄 Download as CSV", csv, "flashcards.csv", "text/csv")

        # Anki TSV export
        tsv = df.to_csv(index=False, sep="\t", header=False).encode('utf-8')
        st.download_button("🧠 Download for Anki", tsv, "anki_flashcards.txt", "text/tab-separated-values")
