import streamlit as st

def show_settings():
    st.set_page_config(layout="wide")
    st.title("⚙️ Settings")

    st.markdown("Customize your CodeMate experience. Toggle features below:")

    with st.form("settings_form"):
        col1, col2 = st.columns(2)

        with col1:
            tip_toggle = st.toggle("💡 Daily Motivational Tips", value=st.session_state.get("show_tips", True))
            pie_toggle = st.toggle("📊 Progress Pie Chart", value=st.session_state.get("show_pie", True))
            time_toggle = st.toggle("🗓 Weekly Time Tracking", value=st.session_state.get("show_time", True))

        with col2:
            streak_toggle = st.toggle("🔥 Productivity Streaks & Badges", value=st.session_state.get("show_streak", True))
            heatmap_toggle = st.toggle("📆 Calendar Heatmap", value=st.session_state.get("show_heatmap", True))
            auto_log_toggle = st.toggle("📝 Auto Log Session in Planner", value=st.session_state.get("auto_log", True))

        submitted = st.form_submit_button("Save Settings")

    if submitted:
        st.session_state["show_tips"] = tip_toggle
        st.session_state["show_pie"] = pie_toggle
        st.session_state["show_time"] = time_toggle
        st.session_state["show_streak"] = streak_toggle
        st.session_state["show_heatmap"] = heatmap_toggle
        st.session_state["auto_log"] = auto_log_toggle

        st.success("✅ Settings updated successfully!")