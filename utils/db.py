import streamlit as st
from supabase import create_client, Client
from datetime import date, datetime
from typing import Optional

_client: Optional[Client] = None


def get_client() -> Client:
    global _client
    if _client is None:
        _client = create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"],
        )
    return _client


# ── Technicians ──────────────────────────────────────────────────────────────

def get_technicians(active_only: bool = True) -> list[dict]:
    db = get_client()
    q = db.table("technicians").select("*").order("name")
    if active_only:
        q = q.eq("active", True)
    return q.execute().data


def get_all_technicians() -> list[dict]:
    return get_technicians(active_only=False)


def add_technician(name: str, phone: str = "") -> dict:
    db = get_client()
    return db.table("technicians").insert({"name": name, "phone": phone}).execute().data[0]


def toggle_technician_active(tech_id: int, active: bool) -> None:
    db = get_client()
    db.table("technicians").update({"active": active}).eq("id", tech_id).execute()


# ── Customers ────────────────────────────────────────────────────────────────

def get_customers(search: str = "") -> list[dict]:
    db = get_client()
    q = db.table("customers").select("*").order("name")
    if search:
        # ilike matches on name OR mobile
        q = q.or_(f"name.ilike.%{search}%,mobile.ilike.%{search}%")
    return q.execute().data


def add_customer(name: str, mobile: str = "", address: str = "",
                 email: str = "", notes: str = "") -> dict:
    db = get_client()
    row = {"name": name}
    if mobile:
        row["mobile"] = mobile
    if address:
        row["address"] = address
    if email:
        row["email"] = email
    if notes:
        row["notes"] = notes
    return db.table("customers").insert(row).execute().data[0]


def get_customer_by_id(customer_id: int) -> Optional[dict]:
    db = get_client()
    rows = db.table("customers").select("*").eq("id", customer_id).execute().data
    return rows[0] if rows else None


# ── Visits ───────────────────────────────────────────────────────────────────

def add_visit(customer_id: int, visit_date: date, notes: str = "") -> int:
    db = get_client()
    row = {"customer_id": customer_id, "visit_date": str(visit_date)}
    if notes:
        row["notes"] = notes
    return db.table("visits").insert(row).execute().data[0]["id"]


# ── Jobs ─────────────────────────────────────────────────────────────────────

def add_job(visit_id: int, service_name: str, technician_id: int,
            cost: float, payment_method: str, notes: str = "") -> dict:
    db = get_client()
    row = {
        "visit_id": visit_id,
        "service_name": service_name,
        "technician_id": technician_id,
        "job_datetime": datetime.now().isoformat(),
        "cost": cost,
        "payment_method": payment_method,
    }
    if notes:
        row["notes"] = notes
    return db.table("jobs").insert(row).execute().data[0]


def get_jobs_for_customer(customer_id: int) -> list[dict]:
    """Returns jobs joined with visit date and technician name for a customer."""
    db = get_client()
    return (
        db.table("jobs")
        .select("*, visits!inner(visit_date, customer_id), technicians(name)")
        .eq("visits.customer_id", customer_id)
        .order("job_datetime", desc=True)
        .execute()
        .data
    )


# ── Analytics ────────────────────────────────────────────────────────────────

def get_jobs_in_period(start: date, end: date) -> list[dict]:
    """Returns all jobs (with technician name) between start and end dates inclusive."""
    db = get_client()
    return (
        db.table("jobs")
        .select("*, visits!inner(visit_date), technicians(name)")
        .gte("visits.visit_date", str(start))
        .lte("visits.visit_date", str(end))
        .order("job_datetime", desc=True)
        .execute()
        .data
    )


def get_jobs_for_technician_in_period(tech_id: int, start: date, end: date) -> list[dict]:
    db = get_client()
    return (
        db.table("jobs")
        .select("*, visits!inner(visit_date), technicians(name)")
        .eq("technician_id", tech_id)
        .gte("visits.visit_date", str(start))
        .lte("visits.visit_date", str(end))
        .order("job_datetime", desc=True)
        .execute()
        .data
    )
