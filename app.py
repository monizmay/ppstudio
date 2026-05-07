import streamlit as st
import utils.db as db

st.set_page_config(page_title="PP Studio", page_icon="💅", layout="wide")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

login_page       = st.Page("pages/login.py",         title="Login")
new_visit_page   = st.Page("pages/1_New_Visit.py",   title="New Visit")
customers_page   = st.Page("pages/2_Customers.py",   title="Customers")
technicians_page = st.Page("pages/3_Technicians.py", title="Technicians")
analytics_page   = st.Page("pages/4_Analytics.py",   title="Analytics")
approvals_page   = st.Page("pages/6_Approvals.py",   title="Approvals")

if not st.session_state["authenticated"]:
    pg = st.navigation([login_page], position="hidden")
else:
    role = st.session_state.get("role", "")
    if role == "admin":
        try:
            pending_count = len(db.get_pending_jobs())
        except Exception:
            pending_count = 0
        approval_title = f"Approvals ({pending_count})" if pending_count else "Approvals"
        approvals_page = st.Page("pages/6_Approvals.py", title=approval_title)
        pages = [new_visit_page, customers_page, technicians_page, analytics_page, approvals_page]
    else:
        pages = [new_visit_page, analytics_page]
    pg = st.navigation(pages)
    with st.sidebar:
        st.caption(f"Logged in as **{st.session_state.get('user_name', '')}**")
        if st.button("Log Out", use_container_width=True):
            for key in ["authenticated", "role", "user_id", "user_name", "technician_id"]:
                st.session_state.pop(key, None)
            st.rerun()

pg.run()
