import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta
from utils.auth import require_login, is_admin, current_technician_id
import utils.db as db

st.set_page_config(page_title="Analytics — PP Studio", page_icon="💅", layout="wide")
require_login()

st.title("Analytics")
st.divider()


# ── Helpers ───────────────────────────────────────────────────────────────────

def jobs_to_df(jobs: list[dict]) -> pd.DataFrame:
    if not jobs:
        return pd.DataFrame()
    rows = []
    for j in jobs:
        rows.append({
            "Date": j["visits"]["visit_date"],
            "Service": j["service_name"],
            "Technician": j["technicians"]["name"] if j.get("technicians") else "—",
            "Cost (₹)": float(j["cost"]),
            "Payment": j["payment_method"],
        })
    return pd.DataFrame(rows)


def period_dates(label: str) -> tuple[date, date]:
    today = date.today()
    if label == "Today":
        return today, today
    if label == "This Week":
        start = today - timedelta(days=today.weekday())
        return start, today
    if label == "This Month":
        return today.replace(day=1), today
    return today, today


def render_technician_tab(tech_id: int | None, tech_name: str, show_selector: bool):
    if show_selector:
        technicians = db.get_all_technicians()
        if not technicians:
            st.info("No technicians found.")
            return
        tech_options = {t["name"]: t["id"] for t in technicians}
        tech_name = st.selectbox("Select Technician", list(tech_options.keys()))
        tech_id = tech_options[tech_name]

    if not tech_id:
        st.error("Technician account is not linked to a technician record. Contact admin.")
        return

    period_t = st.radio(
        "Period",
        ["Today", "This Week", "This Month", "Custom Range"],
        horizontal=True,
        key="tech_period",
    )
    if period_t == "Custom Range":
        col1, col2 = st.columns(2)
        t_start = col1.date_input("From", value=date.today() - timedelta(days=7), key="ts")
        t_end = col2.date_input("To", value=date.today(), key="te")
    else:
        t_start, t_end = period_dates(period_t)

    t_jobs = db.get_jobs_for_technician_in_period(tech_id, t_start, t_end)
    t_df = jobs_to_df(t_jobs)

    if t_df.empty:
        st.info(f"No jobs for {tech_name} in this period.")
    else:
        total_rev = t_df["Cost (₹)"].sum()
        m1, m2 = st.columns(2)
        m1.metric("Jobs Completed", len(t_df))
        m2.metric("Revenue Generated", f"₹{total_rev:,.0f}")
        st.divider()
        st.markdown("**Service Breakdown**")
        svc_t = t_df.groupby("Service")["Cost (₹)"].agg(["count", "sum"]).reset_index()
        svc_t.columns = ["Service", "Count", "Revenue (₹)"]
        st.dataframe(svc_t, use_container_width=True, hide_index=True)
        st.markdown("**All Jobs**")
        st.dataframe(t_df, use_container_width=True, hide_index=True)


# ── Admin: 3 tabs ─────────────────────────────────────────────────────────────
if is_admin():
    tab_summary, tab_technician, tab_customer = st.tabs(
        ["Summary", "By Technician", "Customer History"]
    )

    with tab_summary:
        st.subheader("Revenue Summary")
        period_choice = st.radio(
            "Period",
            ["Today", "This Week", "This Month", "Custom Range"],
            horizontal=True,
        )
        if period_choice == "Custom Range":
            col1, col2 = st.columns(2)
            start_date = col1.date_input("From", value=date.today() - timedelta(days=7))
            end_date = col2.date_input("To", value=date.today())
        else:
            start_date, end_date = period_dates(period_choice)

        jobs = db.get_jobs_in_period(start_date, end_date)
        df = jobs_to_df(jobs)

        if df.empty:
            st.info("No jobs recorded for this period.")
        else:
            total_revenue = df["Cost (₹)"].sum()
            total_jobs = len(df)
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Revenue", f"₹{total_revenue:,.0f}")
            m2.metric("Total Jobs", total_jobs)
            m3.metric("Avg per Job", f"₹{total_revenue / total_jobs:,.0f}")
            st.divider()
            col_l, col_r = st.columns(2)
            with col_l:
                st.markdown("**Revenue by Service**")
                svc_df = df.groupby("Service")["Cost (₹)"].sum().reset_index().sort_values("Cost (₹)", ascending=False)
                fig = px.bar(svc_df, x="Service", y="Cost (₹)", text_auto=True, color="Service")
                fig.update_layout(showlegend=False, margin=dict(t=20, b=0))
                st.plotly_chart(fig, use_container_width=True)
            with col_r:
                st.markdown("**Revenue by Technician**")
                tech_df = df.groupby("Technician")["Cost (₹)"].sum().reset_index().sort_values("Cost (₹)", ascending=False)
                fig2 = px.pie(tech_df, names="Technician", values="Cost (₹)", hole=0.4)
                fig2.update_layout(margin=dict(t=20, b=0))
                st.plotly_chart(fig2, use_container_width=True)
            st.markdown("**All Jobs**")
            st.dataframe(df, use_container_width=True, hide_index=True)

    with tab_technician:
        st.subheader("Technician Performance")
        render_technician_tab(tech_id=0, tech_name="", show_selector=True)

    with tab_customer:
        st.subheader("Customer Service History")
        search = st.text_input("Search customer by name or mobile number", key="cust_search")
        if search:
            customers = db.get_customers(search=search)
            if not customers:
                st.info("No customers found.")
            else:
                options = {f"{c['name']} ({c.get('mobile', 'no mobile')})": c["id"] for c in customers}
                choice = st.selectbox("Select customer", list(options.keys()))
                cust_id = options[choice]
                c_jobs = db.get_jobs_for_customer(cust_id)
                c_df = jobs_to_df(c_jobs)
                if c_df.empty:
                    st.info("No service history for this customer.")
                else:
                    total_spent = c_df["Cost (₹)"].sum()
                    m1, m2 = st.columns(2)
                    m1.metric("Total Visits/Services", len(c_df))
                    m2.metric("Total Spent", f"₹{total_spent:,.0f}")
                    st.dataframe(c_df, use_container_width=True, hide_index=True)
        else:
            st.info("Enter a name or mobile number to search.")

# ── Technician: my jobs only ──────────────────────────────────────────────────
else:
    tab_technician, = st.tabs(["My Jobs"])
    with tab_technician:
        st.subheader("My Performance")
        my_id = current_technician_id()
        my_name = st.session_state.get("user_name", "")
        render_technician_tab(tech_id=my_id, tech_name=my_name, show_selector=False)
