import streamlit as st

st.set_page_config(page_title="PP Studio", page_icon="💅", layout="wide")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

login_page       = st.Page("pages/login.py",         title="Login")
new_visit_page   = st.Page("pages/1_New_Visit.py",   title="New Visit")
customers_page   = st.Page("pages/2_Customers.py",   title="Customers")
technicians_page = st.Page("pages/3_Technicians.py", title="Technicians")
analytics_page   = st.Page("pages/4_Analytics.py",   title="Analytics")

if not st.session_state["authenticated"]:
    pg = st.navigation([login_page], position="hidden")
else:
    role = st.session_state.get("role", "")
    if role == "admin":
        pages = [new_visit_page, customers_page, technicians_page, analytics_page]
    else:
        pages = [new_visit_page, customers_page, analytics_page]
    pg = st.navigation(pages)

pg.run()
