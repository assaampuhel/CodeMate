import streamlit as st
import sqlite3
import json
import pandas as pd
import datetime
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.colored_header import colored_header
import plotly.express as px
import openai
import os
from collections import Counter

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_daily_tip():
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a motivational assistant."},
                {"role": "user", "content": "Give a short motivational tip for a college student learning to code."}
            ],
            max_tokens=60,
            temperature=0.7
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception:
        return "Keep going — every line of code you write makes you better!"

def create_study_log_table():
    conn = sqlite3.connect("data/user_data.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS study_log (
            username TEXT,
            study_date TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_study_session(username, study_date):
    conn = sqlite3.connect("data/user_data.db")
    c = conn.cursor()
    c.execute("INSERT INTO study_log (username, study_date) VALUES (?, ?)", (username, study_date))
    conn.commit()
    conn.close()

def get_weekly_study_data(username):
    today = datetime.date.today()
    last_7_days = [(today - datetime.timedelta(days=i)).isoformat() for i in range(6, -1, -1)]
    conn = sqlite3.connect("data/user_data.db")
    c = conn.cursor()
    c.execute("SELECT study_date FROM study_log WHERE username = ?", (username,))
    rows = c.fetchall()
    conn.close()
    day_counts = {d: 0 for d in last_7_days}
    for row in rows:
        date_str = row[0]
        if date_str in day_counts:
            day_counts[date_str] += 1
    return [(datetime.date.fromisoformat(d).strftime("%A"), count) for d, count in day_counts.items()]

def show_dashboard():
    st.set_page_config(layout="wide")
    st.title("📊 Your Learning Dashboard")

    username = st.session_state.get("username", "guest")

    create_study_log_table()

    # Motivational Quote Section
    tip = get_daily_tip()
    st.markdown(f"💡 **Daily Tip:** _{tip}_")

    today = datetime.date.today()
    if st.button("📌 Log Today’s Study Session"):
        log_study_session(username, today.isoformat())
        st.success("✅ Study session logged for today!")

    colored_header(
        label=f"Welcome back, {username}!",
        description="Here’s an overview of your programming journey. Keep up the momentum!",
        color_name="violet-70",
    )

    try:
        conn = sqlite3.connect("data/user_data.db")
        c = conn.cursor()
        c.execute("SELECT language, goal, start_date, end_date, plan_json FROM planner WHERE username = ?", (username,))
        row = c.fetchone()
        conn.close()

        if row:
            language, goal, start_date, end_date, plan_json = row
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
            total_days = (end_date - start_date).days
            days_left = (end_date - today).days
            days_spent = max(0, (today - start_date).days)

            plan = json.loads(plan_json)
            total_topics = len(plan)
            completed_topics = sum(1 for d in plan if datetime.date.fromisoformat(d) < today)
            completion_pct = int((completed_topics / total_topics) * 100)

            with st.container():
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📚 Language", language)
                with col2:
                    st.metric("🎯 Goal", goal)
                with col3:
                    st.metric("📅 Days Remaining", f"{days_left} days")

                style_metric_cards()

            st.markdown("#### 📈 Your Progress")
            st.progress(completion_pct, text=f"{completion_pct}% Complete")

            # Pie chart for topic completion breakdown
            st.markdown("#### 📊 Topic Completion Breakdown")
            labels = ["Completed", "Remaining"]
            values = [completed_topics, total_topics - completed_topics]
            fig = px.pie(names=labels, values=values, title="Study Progress")
            st.plotly_chart(fig, use_container_width=True)

            # --- Weekly Study Session Bar Chart ---
            st.markdown("#### 📅 Weekly Time Tracking")
            # Simulated weekly study session count (replace with real data if available)
            study_data = {
                "Day": [(today - datetime.timedelta(days=i)).strftime("%A") for i in reversed(range(7))],
                "Study Sessions": [1, 1, 0, 1, 1, 0, 1]  # Simulated: can be replaced with real data
            }
            df_sessions = pd.DataFrame(study_data)
            fig_bar = px.bar(df_sessions, x="Day", y="Study Sessions", title="Sessions in the Last 7 Days")
            st.plotly_chart(fig_bar, use_container_width=True)

            # --- Productivity Streak Tracker ---
            st.markdown("#### 🔥 Productivity Streak")
            streak = 0
            # plan: dict with keys as ISO date strings
            for i in reversed(range(7)):
                day = (today - datetime.timedelta(days=i)).isoformat()
                if day in plan:
                    streak += 1
                else:
                    streak = 0
            if streak > 0:
                st.success(f"🔥 You're on a {streak}-day streak!")
                if streak >= 7:
                    st.balloons()
                    st.markdown("🏅 **Badge Earned:** 1-Week Coding Warrior!")
                elif streak >= 3:
                    st.markdown("🥉 **Badge Earned:** 3-Day Streak Champ!")
            else:
                st.info("Start studying today to build your streak!")

            st.divider()
            st.markdown("### 📌 Weekly Overview")

            upcoming = {
                d: plan[d] for d in list(plan.keys())
                if today <= datetime.date.fromisoformat(d) <= today + datetime.timedelta(days=6)
            }

            if upcoming:
                df = pd.DataFrame(list(upcoming.items()), columns=["Date", "Topic"])
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("🎉 You have no planned topics for this week. Enjoy a break or add more!")

            st.divider()
            st.markdown("### 🗂️ Full Study Plan")
            all_plan = pd.DataFrame(list(plan.items()), columns=["Date", "Topic"])
            st.dataframe(all_plan, use_container_width=True, height=300)

            # --- Real Weekly Time Tracking using study_log table ---
            st.markdown("#### 📅 Weekly Time Tracking (Logged Sessions)")
            weekly_data = get_weekly_study_data(username)
            df_sessions = pd.DataFrame(weekly_data, columns=["Day", "Study Sessions"])
            fig_bar = px.bar(df_sessions, x="Day", y="Study Sessions", title="Sessions in the Last 7 Days")
            st.plotly_chart(fig_bar, use_container_width=True)

            # --- Real Productivity Streak using study_log table ---
            st.markdown("#### 🔥 Productivity Streak")
            streak = 0
            conn = sqlite3.connect("data/user_data.db")
            c = conn.cursor()
            c.execute("SELECT study_date FROM study_log WHERE username = ?", (username,))
            study_dates = set(row[0] for row in c.fetchall())
            conn.close()
            for i in reversed(range(7)):
                day = (today - datetime.timedelta(days=i)).isoformat()
                if day in study_dates:
                    streak += 1
                else:
                    break
            if streak > 0:
                st.success(f"🔥 You're on a {streak}-day streak!")
                if streak >= 7:
                    st.balloons()
                    st.markdown("🏅 **Badge Earned:** 1-Week Coding Warrior!")
                elif streak >= 3:
                    st.markdown("🥉 **Badge Earned:** 3-Day Streak Champ!")
            else:
                st.info("Start studying today to build your streak!")

            # --- Calendar Heatmap for study activity ---
            st.markdown("#### 📆 Study Activity Calendar")

            if study_dates:
                date_list = list(study_dates)
                study_counts = Counter(date_list)
                calendar_df = pd.DataFrame({
                    "date": list(study_counts.keys()),
                    "count": list(study_counts.values())
                })
                calendar_df["date"] = pd.to_datetime(calendar_df["date"])
                calendar_df["day"] = calendar_df["date"].dt.day
                calendar_df["week"] = calendar_df["date"].dt.isocalendar().week
                calendar_df["month"] = calendar_df["date"].dt.month

                fig_heatmap = px.density_heatmap(
                    calendar_df,
                    x="week",
                    y="day",
                    z="count",
                    nbinsx=52,
                    nbinsy=31,
                    color_continuous_scale="Viridis",
                    title="Your Coding Activity Calendar"
                )
                st.plotly_chart(fig_heatmap, use_container_width=True)
            else:
                st.info("📭 No study sessions logged yet for calendar view.")

        else:
            st.warning("⚠️ No study plan found. Please create one in the Planner tab.")

    except Exception as e:
        st.error(f"Something went wrong while loading the dashboard: {e}")
