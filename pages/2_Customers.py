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
                approved_jobs = [j for j in jobs if j.get("approved")]
                pending_jobs  = [j for j in jobs if not j.get("approved")]
                total = sum(j["cost"] for j in approved_jobs)

                if is_admin():
                    # Show delete feedback for this customer
                    _del_status = st.session_state.pop(f"job_delete_status_{cust['id']}", None)
                    if _del_status:
                        st.success(_del_status, icon="✅")

                    # Pending confirmation banner
                    _pending = st.session_state.get("confirm_delete_job")
                    if _pending and any(j["id"] == _pending for j in jobs):
                        st.warning("Delete this job record? This cannot be undone.")
                        _c1, _c2, _ = st.columns([1, 1, 6])
                        if _c1.button("Confirm", key=f"confirm_{_pending}", type="primary"):
                            db.delete_job(_pending)
                            del st.session_state["confirm_delete_job"]
                            st.session_state[f"job_delete_status_{cust['id']}"] = "Job deleted successfully."
                            st.rerun()
                        if _c2.button("Cancel", key=f"cancel_{_pending}"):
                            del st.session_state["confirm_delete_job"]
                            st.rerun()

                    # Row-by-row layout with delete button
                    hc = st.columns([2, 3, 2, 1, 1, 3, 1, 0.5])
                    for h, label in zip(hc[:-1], ["Date", "Service", "Technician", "Cost (₹)", "Payment", "Notes", "Status"]):
                        h.caption(label)
                    for j in approved_jobs:
                        rc = st.columns([2, 3, 2, 1, 1, 3, 1, 0.5])
                        rc[0].write(j["visits"]["visit_date"])
                        rc[1].write(j["service_name"])
                        rc[2].write(j["technicians"]["name"] if j.get("technicians") else "—")
                        rc[3].write(f"₹{j['cost']:,.0f}")
                        rc[4].write(j["payment_method"])
                        rc[5].write(j.get("notes") or "")
                        rc[6].write(":green[✅ Approved]")
                        if rc[7].button("🗑", key=f"del_{j['id']}", help="Delete this job"):
                            st.session_state["confirm_delete_job"] = j["id"]
                            st.rerun()
                    for j in pending_jobs:
                        rc = st.columns([2, 3, 2, 1, 1, 3, 1, 0.5])
                        rc[0].write(j["visits"]["visit_date"])
                        rc[1].write(j["service_name"])
                        rc[2].write(j["technicians"]["name"] if j.get("technicians") else "—")
                        rc[3].write(f"₹{j['cost']:,.0f}")
                        rc[4].write(j["payment_method"])
                        rc[5].write(j.get("notes") or "")
                        rc[6].write(":orange[⏳ Pending]")
                        if rc[7].button("🗑", key=f"del_{j['id']}", help="Delete this job"):
                            st.session_state["confirm_delete_job"] = j["id"]
                            st.rerun()
                else:
                    rows = [
                        {
                            "Date": j["visits"]["visit_date"],
                            "Service": j["service_name"],
                            "Technician": j["technicians"]["name"] if j.get("technicians") else "—",
                            "Cost (₹)": j["cost"],
                            "Payment": j["payment_method"],
                            "Notes": j.get("notes") or "",
                            "Status": "✅ Approved" if j.get("approved") else "⏳ Pending",
                        }
                        for j in jobs
                    ]
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

                st.write(f"**Total spent: ₹{total:,.0f}** across {len(approved_jobs)} approved service(s)"
                         + (f" · {len(pending_jobs)} pending" if pending_jobs else ""))
