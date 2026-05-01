import streamlit as st
from datetime import date
from utils.auth import require_login, is_admin, current_technician_id
from utils.constants import SERVICES, PAYMENT_METHODS, PAYMENT_METHOD_MAP
import utils.db as db

st.set_page_config(page_title="New Visit — PP Studio", page_icon="💅", layout="wide")
require_login()

# ── Visit summary (shown after successful submit) ─────────────────────────────
if "visit_summary" in st.session_state:
    summary = st.session_state["visit_summary"]
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
        st.rerun()
    st.stop()

# ── New visit form ────────────────────────────────────────────────────────────
st.title("New Visit")
st.divider()

if "job_count" not in st.session_state:
    st.session_state["job_count"] = 1

if st.button("+ Add Another Job"):
    st.session_state["job_count"] += 1

if st.button("- Remove Last Job") and st.session_state["job_count"] > 1:
    st.session_state["job_count"] -= 1

# ── Customer selection ────────────────────────────────────────────────────────
st.subheader("Customer")

customer_mode = st.radio(
    "Customer",
    ["Search existing", "Add new customer"],
    horizontal=True,
    label_visibility="collapsed",
)

selected_customer_id = None

if customer_mode == "Search existing":
    search_term = st.text_input("Search by name or mobile number")
    customers = db.get_customers(search=search_term)
    if customers:
        options = {f"{c['name']} ({c.get('mobile', 'no mobile')})": c["id"] for c in customers}
        choice = st.selectbox("Select customer", list(options.keys()))
        selected_customer_id = options[choice]
    else:
        st.info("No customers found. Try a different search or add a new customer.")
else:
    with st.form("new_customer_form"):
        col1, col2 = st.columns(2)
        new_name = col1.text_input("Full Name *")
        new_mobile = col2.text_input("Mobile Number")
        new_address = st.text_input("Address")
        col3, col4 = st.columns(2)
        new_email = col3.text_input("Email")
        new_notes = col4.text_input("Notes")
        save_customer = st.form_submit_button("Save Customer", use_container_width=True)

    if save_customer:
        if not new_name.strip():
            st.error("Customer name is required.")
        else:
            cust = db.add_customer(
                name=new_name.strip(),
                mobile=new_mobile.strip(),
                address=new_address.strip(),
                email=new_email.strip(),
                notes=new_notes.strip(),
            )
            st.session_state["new_customer_id"] = cust["id"]
            st.session_state["new_customer_name"] = cust["name"]
            st.success(f"Customer '{cust['name']}' saved.")

    if "new_customer_id" in st.session_state:
        selected_customer_id = st.session_state["new_customer_id"]
        st.info(f"Using new customer: **{st.session_state['new_customer_name']}**")

# ── Visit date ────────────────────────────────────────────────────────────────
st.subheader("Visit Details")
visit_date = st.date_input("Visit Date", value=date.today())
visit_notes = st.text_input("Visit Notes (optional)")

# ── Jobs ──────────────────────────────────────────────────────────────────────
st.subheader(f"Jobs ({st.session_state['job_count']})")

technicians = db.get_technicians()
tech_options = {t["name"]: t["id"] for t in technicians}
tech_id_to_name = {t["id"]: t["name"] for t in technicians}

job_entries = []
for i in range(st.session_state["job_count"]):
    st.markdown(f"**Job {i + 1}**")
    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
    service = col1.selectbox("Service", SERVICES, key=f"service_{i}")
    if is_admin():
        tech_name = col2.selectbox("Technician", list(tech_options.keys()), key=f"tech_{i}")
        tech_id = tech_options[tech_name]
    else:
        my_id = current_technician_id()
        col2.write(f"**Technician:** {tech_id_to_name.get(my_id, 'Unknown')}")
        tech_id = my_id
    cost = col3.number_input("Cost (₹)", min_value=0.0, step=50.0, key=f"cost_{i}")
    payment = col4.selectbox("Payment", PAYMENT_METHODS, key=f"payment_{i}")
    job_note = st.text_input("Job Notes (optional)", key=f"jobnote_{i}")
    job_entries.append({
        "service": service,
        "tech_id": tech_id,
        "cost": cost,
        "payment": PAYMENT_METHOD_MAP[payment],
        "note": job_note,
    })
    if i < st.session_state["job_count"] - 1:
        st.divider()

# ── Submit ────────────────────────────────────────────────────────────────────
st.divider()
if st.button("Submit Visit", type="primary", use_container_width=True):
    if selected_customer_id is None:
        st.error("Please select or create a customer first.")
    elif not job_entries:
        st.error("Please add at least one job.")
    else:
        try:
            with st.spinner("Saving visit..."):
                visit_id = db.add_visit(
                    customer_id=selected_customer_id,
                    visit_date=visit_date,
                    notes=visit_notes.strip(),
                )
                for job in job_entries:
                    db.add_job(
                        visit_id=visit_id,
                        service_name=job["service"],
                        technician_id=job["tech_id"],
                        cost=job["cost"],
                        payment_method=job["payment"],
                        notes=job["note"].strip(),
                    )
            customer = db.get_customer_by_id(selected_customer_id)
            st.session_state["visit_summary"] = {
                "visit_id": visit_id,
                "customer_name": customer["name"] if customer else "Unknown",
                "customer_mobile": customer.get("mobile", "") if customer else "",
                "visit_date": str(visit_date),
                "visit_notes": visit_notes.strip(),
                "jobs": [
                    {
                        "service": j["service"],
                        "tech_name": tech_id_to_name.get(j["tech_id"], "Unknown"),
                        "cost": j["cost"],
                        "payment": j["payment"],
                        "note": j["note"],
                    }
                    for j in job_entries
                ],
                "total": sum(j["cost"] for j in job_entries),
            }
            st.session_state["job_count"] = 1
            if "new_customer_id" in st.session_state:
                del st.session_state["new_customer_id"]
                del st.session_state["new_customer_name"]
            st.rerun()
        except Exception as e:
            st.error(f"Failed to save visit. Please try again. ({e})")
