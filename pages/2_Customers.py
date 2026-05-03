import streamlit as st
import pandas as pd
from utils.auth import require_login, is_admin, current_technician_id
import utils.db as db

st.set_page_config(page_title="Customers — PP Studio", page_icon="💅", layout="wide")
require_login()

st.title("Customers")
st.divider()

# ── Search ────────────────────────────────────────────────────────────────────
search = st.text_input("Search by name or mobile number", placeholder="e.g. Priya or 9876543210")
customers = db.get_customers(search=search)

# ── Add Customer ──────────────────────────────────────────────────────────────
with st.expander("Add New Customer"):
    _status = st.session_state.pop("customer_add_status", None)
    if _status:
        if _status["ok"]:
            st.success(_status["msg"], icon="✅")
        else:
            st.error(_status["msg"], icon="❌")

    with st.form("add_customer_form"):
        col1, col2 = st.columns(2)
        name = col1.text_input("Full Name *")
        mobile = col2.text_input("Mobile Number")
        address = st.text_input("Address")
        col3, col4 = st.columns(2)
        email = col3.text_input("Email")
        notes = col4.text_input("Notes")
        submitted = st.form_submit_button("Add Customer", use_container_width=True)

    if submitted:
        if not name.strip():
            st.session_state["customer_add_status"] = {"ok": False, "msg": "Customer name is required."}
        else:
            db.add_customer(
                name=name.strip(),
                mobile=mobile.strip(),
                address=address.strip(),
                email=email.strip(),
                notes=notes.strip(),
            )
            st.session_state["customer_add_status"] = {"ok": True, "msg": f"Customer '{name.strip()}' added successfully."}
        st.rerun()

st.divider()

# ── Customer list ─────────────────────────────────────────────────────────────
if not customers:
    st.info("No customers found.")
else:
    st.write(f"**{len(customers)} customer(s) found**")
    for cust in customers:
        label = f"{cust['name']}"
        if cust.get("mobile"):
            label += f" — {cust['mobile']}"
        with st.expander(label):
            if is_admin():
                col1, col2 = st.columns(2)
                col1.write(f"**Address:** {cust.get('address') or '—'}")
                col1.write(f"**Email:** {cust.get('email') or '—'}")
                col2.write(f"**Notes:** {cust.get('notes') or '—'}")
                col2.write(f"**Customer since:** {str(cust.get('created_at', ''))[:10]}")

            st.markdown("##### Service History")
            jobs = db.get_jobs_for_customer(cust["id"])

            if not is_admin():
                my_id = current_technician_id()
                jobs = [j for j in jobs if j.get("technician_id") == my_id]

            if not jobs:
                st.write("No visits recorded yet.")
            else:
                rows = []
                for j in jobs:
                    rows.append({
                        "Date": j["visits"]["visit_date"],
                        "Service": j["service_name"],
                        "Technician": j["technicians"]["name"] if j.get("technicians") else "—",
                        "Cost (₹)": j["cost"],
                        "Payment": j["payment_method"],
                        "Notes": j.get("notes") or "",
                    })
                df = pd.DataFrame(rows)
                total = df["Cost (₹)"].sum()
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.write(f"**Total spent: ₹{total:,.0f}** across {len(rows)} service(s)")
