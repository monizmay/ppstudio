import streamlit as st
import pandas as pd
from utils.auth import require_login
import utils.db as db

st.set_page_config(page_title="Technicians — PP Studio", page_icon="💅", layout="wide")
require_login()

st.title("Technicians")
st.divider()

# ── Add Technician ────────────────────────────────────────────────────────────
with st.expander("Add New Technician"):
    with st.form("add_tech_form"):
        col1, col2 = st.columns(2)
        name = col1.text_input("Name *")
        phone = col2.text_input("Phone Number")
        submitted = st.form_submit_button("Add Technician", use_container_width=True)

    if submitted:
        if not name.strip():
            st.error("Technician name is required.")
        else:
            db.add_technician(name=name.strip(), phone=phone.strip())
            st.success(f"Technician '{name.strip()}' added.")
            st.rerun()

st.divider()

# ── Technician list ───────────────────────────────────────────────────────────
technicians = db.get_all_technicians()

if not technicians:
    st.info("No technicians yet. Add one above.")
else:
    for tech in technicians:
        col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
        col1.write(f"**{tech['name']}**")
        col2.write(tech.get("phone") or "—")
        status_label = "Active" if tech["active"] else "Inactive"
        col3.write(f":{('green' if tech['active'] else 'red')}[{status_label}]")
        toggle_label = "Deactivate" if tech["active"] else "Activate"
        if col4.button(toggle_label, key=f"toggle_{tech['id']}"):
            db.toggle_technician_active(tech["id"], not tech["active"])
            st.rerun()
