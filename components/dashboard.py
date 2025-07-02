import streamlit as st
import sqlite3
import json
import pandas as pd
import datetime
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.colored_header import colored_header

def show_dashboard():
    st.set_page_config(layout="wide")
    st.title("📊 Your Learning Dashboard")

    username = st.session_state.get("username", "guest")

    colored_header(
        label=f"Welcome back, {username}!",
        description="Here’s an overview of your programming journey.",
        color_name="blue-70",
    )

    col1, col2, col3 = st.columns(3)

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
            today = datetime.date.today()
            total_days = (end_date - start_date).days
            days_left = (end_date - today).days
            days_spent = max(0, (today - start_date).days)

            plan = json.loads(plan_json)
            total_topics = len(plan)
            completed_topics = sum(1 for d in plan if datetime.date.fromisoformat(d) < today)
            completion_pct = int((completed_topics / total_topics) * 100)

            with col1:
                st.metric("📚 Language", language)
            with col2:
                st.metric("🎯 Goal", goal)
            with col3:
                st.metric("📅 Days Remaining", f"{days_left} days")

            st.progress(completion_pct, text=f"{completion_pct}% Complete")

            style_metric_cards()

            st.divider()
            st.subheader("🧭 Weekly Overview")

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
            st.subheader("📆 Full Plan (Condensed View)")
            all_plan = pd.DataFrame(list(plan.items()), columns=["Date", "Topic"])
            st.dataframe(all_plan, use_container_width=True, height=300)

        else:
            st.warning("No study plan found. Please create one in the Planner tab.")

    except Exception as e:
        st.error(f"Something went wrong: {e}")
