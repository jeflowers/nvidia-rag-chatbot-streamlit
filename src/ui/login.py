"""Login user interface."""

from datetime import datetime, timedelta

import streamlit as st

from src.utils.config import Config
from src.auth.auth_manager import authenticate_user


def login_ui() -> None:
    """Render the login interface."""
    st.title("RAG Q&A Chat Application - Login")
    
    # Check for lockout
    if "lockout_until" in st.session_state and st.session_state.lockout_until:
        if datetime.now() < st.session_state.lockout_until:
            remaining = (st.session_state.lockout_until - datetime.now()).seconds // 60
            st.error(f"Too many failed login attempts. Please try again in {remaining} minutes.")
            return
    
    # Reset lockout if expired
    if "lockout_until" in st.session_state and st.session_state.lockout_until:
        if datetime.now() >= st.session_state.lockout_until:
            st.session_state.lockout_until = None
            st.session_state.login_attempts = 0
    
    # Initialize login attempts counter if not present
    if "login_attempts" not in st.session_state:
        st.session_state.login_attempts = 0
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if authenticate_user(username, password):
                st.success("Login successful!")
                st.experimental_rerun()
            else:
                st.session_state.login_attempts += 1
                if st.session_state.login_attempts >= Config.MAX_LOGIN_ATTEMPTS:
                    st.session_state.lockout_until = datetime.now() + timedelta(minutes=Config.IP_COOLDOWN_MINUTES)
                    st.error(f"Too many failed login attempts. Your access has been locked for {Config.IP_COOLDOWN_MINUTES} minutes.")
                else:
                    st.error(f"Invalid username or password. Attempts remaining: {Config.MAX_LOGIN_ATTEMPTS - st.session_state.login_attempts}")
