import streamlit as st
from utils.auth import require_login

st.set_page_config(page_title="Visit Summary — PP Studio", page_icon="💅", layout="wide")
require_login()

summary = st.session_state.get("visit_summary")
if not summary:
    st.warning("No visit summary to display.")
    if st.button("Go to New Visit"):
        st.switch_page("pages/1_New_Visit.py")
    st.stop()

PAYMENT_DISPLAY = {"CASH": "Cash", "UPI": "UPI/QR"}

st.title("Visit Recorded")
st.success(f"Visit #{summary['visit_id']} saved successfully.")
st.divider()

col1, col2 = st.columns(2)
col1.metric("Customer", summary["customer_name"])
if summary["customer_mobile"]:
    col1.caption(summary["customer_mobile"])
col2.metric("Visit Date", summary["visit_date"])
if summary["visit_notes"]:
    st.info(summary["visit_notes"])

st.subheader(f"Jobs ({len(summary['jobs'])})")
for job in summary["jobs"]:
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([2, 2, 1, 1])
        c1.write(f"**{job['service']}**")
        c2.write(job["tech_name"])
        c3.write(f"₹{job['cost']:,.0f}")
        c4.write(PAYMENT_DISPLAY.get(job["payment"], job["payment"]))
        if job["note"]:
            st.caption(job["note"])

st.divider()
st.metric("Total", f"₹{summary['total']:,.0f}")

if st.button("Record Another Visit", type="primary", use_container_width=True):
    del st.session_state["visit_summary"]
    st.switch_page("pages/1_New_Visit.py")
