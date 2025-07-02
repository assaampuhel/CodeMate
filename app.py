import streamlit as st
from auth.login import login_ui
from components.dashboard import show_dashboard
from components.planner import show_planner
from components.summarizer import show_summarizer
from components.flashcards import show_flashcards
from components.questions import show_question_gen

st.set_page_config(page_title="CodeMate", layout="wide")

# Sidebar navigation
menu = st.sidebar.selectbox("Select", ["Login", "Dashboard", "Planner", "Notes Summarizer", "Practice Questions", "Flashcards"])

if menu == "Login":
    login_ui()

elif menu == "Dashboard":
    show_dashboard()

elif menu == "Planner":
    show_planner()

elif menu == "Notes Summarizer":
    show_summarizer()

elif menu == "Practice Questions":
    show_question_gen()

elif menu == "Flashcards":
    show_flashcards()