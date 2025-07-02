import streamlit as st
import sqlite3
import hashlib
from datetime import datetime

DB_PATH = "data/user_data.db"

def create_usertable():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users(
            username TEXT PRIMARY KEY,
            password TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_userdata(username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO users(username, password, created_at) VALUES (?, ?, ?)', 
              (username, password, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    data = c.fetchone()
    conn.close()
    return data

def user_exists(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

def make_hashes(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

def login_ui():
    st.subheader("🔐 Login / Signup")
    create_usertable()

    menu = ["Login", "Sign Up"]
    choice = st.radio("Select Action", menu, horizontal=True)

    if choice == "Login":
        st.markdown("### 🔑 Login")
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type='password', placeholder="Enter your password")

        if st.button("Login"):
            if username and password:
                hashed_pswd = make_hashes(password)
                result = login_user(username, hashed_pswd)
                if result:
                    st.success(f"Welcome back, {username}!")
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username
                else:
                    st.error("❌ Incorrect username or password.")
            else:
                st.warning("Please fill out all fields.")

    elif choice == "Sign Up":
        st.markdown("### 🆕 Create New Account")
        new_user = st.text_input("Choose a Username", placeholder="Create a username")
        new_password = st.text_input("Choose a Password", type='password', placeholder="Create a strong password")

        if st.button("Sign Up"):
            if new_user and new_password:
                if user_exists(new_user):
                    st.warning("⚠️ Username already exists. Try another one.")
                else:
                    add_userdata(new_user, make_hashes(new_password))
                    st.success("✅ Account created successfully!")
                    st.info("Now go to the Login tab to sign in.")
            else:
                st.warning("Please fill out all fields.")
