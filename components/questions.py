

import streamlit as st
from ai.question_gen import generate_questions

def show_question_gen():
    st.set_page_config(layout="wide")
    st.title("❓ Practice Question Generator")
    st.markdown("AI-powered custom programming questions. Select a language and topic to get started.")

    with st.form("question_form"):
        col1, col2 = st.columns(2)
        with col1:
            language = st.selectbox("Programming Language", ["Python", "Java", "C++", "JavaScript"])
        with col2:
            difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])

        topic = st.text_input("Topic (e.g. Recursion, Loops, Classes):")
        num_questions = st.slider("Number of Questions", min_value=1, max_value=10, value=5)

        submitted = st.form_submit_button("Generate Questions")

    if submitted:
        if not topic.strip():
            st.warning("Please enter a topic to generate questions.")
            return

        with st.spinner("Generating questions..."):
            questions = generate_questions(language, topic, difficulty, num_questions)

        if not questions or "question" not in questions[0]:
            st.error("⚠️ Failed to generate questions. Try again.")
            return

        st.success(f"✅ Generated {len(questions)} questions for {language} - {topic} [{difficulty}]")

        for idx, q in enumerate(questions, 1):
            card_color = {
                "MCQ": "#FFF4E5",
                "Short Answer": "#E5F4FF",
                "Coding": "#E8FFE5",
                "Error": "#FFE5E5"
            }.get(q.get("type", "Short Answer"), "#F9F9F9")

            with st.container():
                st.markdown(f"""
                <div style="background-color:{card_color}; padding:15px; border-radius:8px; margin-bottom:10px;">
                    <strong>Q{idx} [{q.get("type")}]:</strong><br>{q.get("question")}
                </div>
                """, unsafe_allow_html=True)