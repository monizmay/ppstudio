import streamlit as st
from utils.auth import require_login

st.set_page_config(page_title="PP Studio", page_icon="💅", layout="wide")
require_login()

st.title("PP Studio — Salon Management")
st.info("Use the sidebar to navigate.")
