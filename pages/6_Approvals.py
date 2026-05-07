import streamlit as st
from utils.auth import require_admin
import utils.db as db

st.set_page_config(page_title="Approvals — PP Studio", page_icon="💅", layout="wide")
require_admin()

st.title("Pending Approvals")
st.divider()

_status = st.session_state.pop("approval_status", None)
if _status:
    st.success(_status, icon="✅")

pending = db.get_pending_jobs()

if not pending:
    st.success("All jobs are approved. Nothing pending.", icon="✅")
else:
    st.info(f"{len(pending)} job(s) awaiting approval")

    hc = st.columns([2, 2, 3, 2, 1, 1, 3, 1])
    for h, label in zip(hc, ["Date", "Customer", "Service", "Technician", "Cost (₹)", "Payment", "Notes", ""]):
        h.caption(label)

    for j in pending:
        rc = st.columns([2, 2, 3, 2, 1, 1, 3, 1])
        rc[0].write(j["visits"]["visit_date"])
        rc[1].write(j["visits"]["customers"]["name"] if j.get("visits", {}).get("customers") else "—")
        rc[2].write(j["service_name"])
        rc[3].write(j["technicians"]["name"] if j.get("technicians") else "—")
        rc[4].write(f"₹{j['cost']:,.0f}")
        rc[5].write(j["payment_method"])
        rc[6].write(j.get("notes") or "")
        if rc[7].button("✅ Approve", key=f"approve_{j['id']}"):
            db.approve_job(j["id"])
            st.session_state["approval_status"] = f"Job approved: {j['service_name']} for {j['visits']['customers']['name']}."
            st.rerun()
