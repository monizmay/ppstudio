import streamlit as st
from utils.auth import check_login

st.set_page_config(
    page_title="PP Studio",
    page_icon="💅",
    layout="centered",
)

# ── Session state init ────────────────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# ── If already logged in, go straight to New Visit ───────────────────────────
if st.session_state["authenticated"]:
    st.switch_page("pages/1_New_Visit.py")

# ── Login form ────────────────────────────────────────────────────────────────
st.title("PP Studio")
st.subheader("Salon Management")
st.divider()

with st.form("login_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Log In", use_container_width=True)

if submitted:
    if check_login(username, password):
        st.session_state["authenticated"] = True
        st.switch_page("pages/1_New_Visit.py")
    else:
        st.error("Invalid username or password.")
