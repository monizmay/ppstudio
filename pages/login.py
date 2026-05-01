import streamlit as st
from utils.auth import check_login

st.title("PP Studio")
st.subheader("Salon Management")
st.divider()

with st.form("login_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Log In", use_container_width=True)

if submitted:
    if check_login(username, password):
        st.rerun()
    else:
        st.error("Invalid username or password.")
