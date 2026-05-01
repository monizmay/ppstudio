import hashlib
import streamlit as st
import utils.db as db


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def check_login(username: str, password: str) -> bool:
    user = db.get_user_by_username(username)
    if not user or not user.get("active"):
        return False
    if user["password_hash"] != hash_password(password):
        return False
    st.session_state["authenticated"] = True
    st.session_state["role"] = user["role"]
    st.session_state["user_id"] = user["id"]
    st.session_state["technician_id"] = user.get("technician_id")
    st.session_state["user_name"] = (
        user["technician_name"] if user.get("technician_name") else username
    )
    return True


def require_login():
    if not st.session_state.get("authenticated"):
        st.switch_page("pages/login.py")
    with st.sidebar:
        st.caption(f"Logged in as **{st.session_state.get('user_name', '')}**")
        if st.button("Log Out", key="sidebar_logout_btn", use_container_width=True):
            for key in ["authenticated", "role", "user_id", "user_name", "technician_id"]:
                st.session_state.pop(key, None)
            st.rerun()


def require_admin():
    require_login()
    if st.session_state.get("role") != "admin":
        st.error("This page is accessible to admins only.")
        st.stop()


def is_admin() -> bool:
    return st.session_state.get("role") == "admin"


def current_technician_id() -> int | None:
    return st.session_state.get("technician_id")
