import streamlit as st
import pandas as pd
import datetime
import json
import os
import sqlite3
from datetime import date

DB_PATH = "data/user_data.db"

def get_user():
    return st.session_state.get("username", "guest")

def create_planner_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS planner(
            username TEXT,
            language TEXT,
            goal TEXT,
            start_date TEXT,
            end_date TEXT,
            total_days INTEGER,
            plan_json TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_plan(username, language, goal, start_date, end_date, total_days, plan_dict):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM planner WHERE username = ?", (username,))
    c.execute('INSERT INTO planner VALUES (?, ?, ?, ?, ?, ?, ?)',
              (username, language, goal, start_date, end_date, total_days, json.dumps(plan_dict)))
    conn.commit()
    conn.close()

def load_user_plan(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM planner WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    return row

def log_study_session(username, study_date):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS study_log (
            username TEXT,
            study_date TEXT
        )
    ''')
    c.execute("INSERT INTO study_log (username, study_date) VALUES (?, ?)", (username, study_date))
    conn.commit()
    conn.close()

def show_planner():
    st.title("📅 Personalized Study Planner")

    create_planner_table()
    username = get_user()

    st.info("This planner helps break down your programming language goals into daily plans.")

    with st.form("planner_form"):
        language = st.selectbox("Which language are you learning?", ["Python", "Java", "C++", "JavaScript"])
        goal = st.text_input("Your Learning Goal (e.g., Crack coding interviews, Learn OOPs, Build Projects)")
        start_date = st.date_input("Start Date", datetime.date.today())
        duration_weeks = st.slider("How many weeks do you want to study?", 1, 12, 4)
        submit = st.form_submit_button("Generate Study Plan")

    if submit:
        total_days = duration_weeks * 7
        end_date = start_date + datetime.timedelta(days=total_days)
        topics = get_language_topics(language)
        plan = create_study_schedule(topics, total_days)

        save_plan(username, language, goal, str(start_date), str(end_date), total_days, plan)
        st.success("Your study plan has been created!")

    # Load and display user plan
    user_plan = load_user_plan(username)
    if user_plan:
        st.subheader(f"📘 Study Plan for {user_plan[1]}")
        st.markdown(f"**Goal:** {user_plan[2]}")
        st.markdown(f"**Start Date:** {user_plan[3]}")
        st.markdown(f"**End Date:** {user_plan[4]}")
        st.markdown(f"**Total Days:** {user_plan[5]}")

        plan_data = json.loads(user_plan[6])
        today_str = str(date.today())
        if today_str in plan_data:
            log_study_session(username, today_str)
            st.success("✅ Today's study session has been automatically logged.")
        df = pd.DataFrame(list(plan_data.items()), columns=["Date", "Topic"])
        st.dataframe(df, use_container_width=True)

def get_language_topics(language):
    base_dir = "data/static_resources"
    file_map = {
        "Python": "py_questions.json",
        "Java": "java_questions.json",
        "C++": "cpp_questions.json",
        "JavaScript": "js_questions.json"
    }
    file_path = os.path.join(base_dir, file_map[language])
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f).get("topics", [])
    else:
        # fallback list
        return [
            "Introduction", "Variables", "Data Types", "Operators", "Control Flow",
            "Functions", "Arrays/Lists", "Strings", "OOP Basics", "Advanced OOP",
            "File Handling", "Error Handling", "Recursion", "Libraries", "Project Work"
        ]

def create_study_schedule(topics, total_days):
    plan = {}
    days = list(pd.date_range(datetime.date.today(), periods=total_days).date)
    step = max(1, total_days // len(topics))
    i = 0
    for day in days:
        if i < len(topics):
            plan[str(day)] = topics[i]
            i += 1 if len(topics) <= total_days else 0
        else:
            plan[str(day)] = "📝 Revision / Practice"
    return plan