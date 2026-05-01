import streamlit as st

HARDCODED_USERNAME = "admin"
HARDCODED_PASSWORD = "admin123"


def check_login(username: str, password: str) -> bool:
    return username == HARDCODED_USERNAME and password == HARDCODED_PASSWORD


def require_login():
    if not st.session_state.get("authenticated"):
        st.warning("Please log in to access this page.")
        st.stop()
