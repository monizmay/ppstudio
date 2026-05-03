import streamlit as st
from utils.auth import require_admin, hash_password
import utils.db as db

st.set_page_config(page_title="Technicians — PP Studio", page_icon="💅", layout="wide")
require_admin()

st.title("Technicians")
st.divider()

# ── Add Technician ────────────────────────────────────────────────────────────
with st.expander("Add New Technician"):
    _status = st.session_state.pop("tech_add_status", None)
    if _status:
        if _status["ok"]:
            st.success(_status["msg"], icon="✅")
        else:
            st.error(_status["msg"], icon="❌")

    with st.form("add_tech_form"):
        col1, col2 = st.columns(2)
        name = col1.text_input("Name *")
        phone = col2.text_input("Phone Number")
        submitted = st.form_submit_button("Add Technician", use_container_width=True)

    if submitted:
        if not name.strip():
            st.session_state["tech_add_status"] = {"ok": False, "msg": "Technician name is required."}
        else:
            tech = db.add_technician(name=name.strip(), phone=phone.strip())
            db.add_user(
                username=name.strip(),
                password_hash=hash_password(name.strip()),
                role="technician",
                technician_id=tech["id"],
            )
            st.session_state["tech_add_status"] = {"ok": True, "msg": f"Technician '{name.strip()}' added. Default login password is their name."}
        st.rerun()

# ── Reset Password ────────────────────────────────────────────────────────────
with st.expander("Reset Technician Password"):
    technicians_all = db.get_all_technicians()
    if not technicians_all:
        st.info("No technicians yet.")
    else:
        with st.form("reset_password_form"):
            tech_options = {t["name"]: t for t in technicians_all}
            selected_name = st.selectbox("Technician", list(tech_options.keys()))
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            reset_submitted = st.form_submit_button("Reset Password", use_container_width=True)

        if reset_submitted:
            if not new_password:
                st.error("Password cannot be empty.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                db.update_user_password(selected_name, hash_password(new_password))
                st.success(f"Password reset for '{selected_name}'.")

st.divider()

# ── Technician list ───────────────────────────────────────────────────────────
technicians = db.get_all_technicians()

if not technicians:
    st.info("No technicians yet. Add one above.")
else:
    header = st.columns([3, 2, 2, 1, 1])
    header[0].caption("Name")
    header[1].caption("Phone")
    header[2].caption("Login Account")
    header[3].caption("Status")
    header[4].caption("")
    st.divider()

    for tech in technicians:
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
        col1.write(f"**{tech['name']}**")
        col2.write(tech.get("phone") or "—")

        user = db.get_user_by_technician_id(tech["id"])
        if user:
            col3.write(f":green[✓ {user['username']}]")
        else:
            if col3.button("Create Login", key=f"create_login_{tech['id']}"):
                db.add_user(
                    username=tech["name"],
                    password_hash=hash_password(tech["name"]),
                    role="technician",
                    technician_id=tech["id"],
                )
                st.success(f"Login created for '{tech['name']}'. Password: '{tech['name']}'")
                st.rerun()

        status_label = "Active" if tech["active"] else "Inactive"
        col4.write(f":{('green' if tech['active'] else 'red')}[{status_label}]")
        toggle_label = "Deactivate" if tech["active"] else "Activate"
        if col5.button(toggle_label, key=f"toggle_{tech['id']}"):
            db.toggle_technician_active(tech["id"], not tech["active"])
            st.rerun()
