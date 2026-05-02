import urllib.parse
from fpdf import FPDF

SALON_NAME = "PP Studio"
PAYMENT_DISPLAY = {"CASH": "Cash", "UPI": "UPI/QR"}


def generate_invoice_pdf(summary: dict) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 15, 15)

    # ── Header ────────────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 24)
    pdf.cell(0, 10, SALON_NAME, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 6, "Invoice", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(5)

    # ── Meta ──────────────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(90, 6, f"Invoice #:  {summary['visit_id']}")
    pdf.cell(0, 6, f"Date:  {summary['visit_date']}", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 10)
    pdf.cell(90, 6, f"Customer:  {summary['customer_name']}")
    if summary.get("customer_mobile"):
        pdf.cell(0, 6, f"Mobile:  {summary['customer_mobile']}", new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.ln(6)

    if summary.get("visit_notes"):
        pdf.set_font("Helvetica", "I", 9)
        pdf.cell(0, 6, f"Notes: {summary['visit_notes']}", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(6)

    # ── Jobs table ────────────────────────────────────────────────────────────
    col_w = [70, 45, 30, 35]
    headers = ["Service", "Technician", "Cost (Rs)", "Payment"]

    pdf.set_fill_color(232, 180, 220)
    pdf.set_font("Helvetica", "B", 10)
    for w, h in zip(col_w, headers):
        pdf.cell(w, 8, h, border=1, fill=True)
    pdf.ln()

    pdf.set_font("Helvetica", "", 10)
    for job in summary["jobs"]:
        pdf.cell(col_w[0], 7, job["service"][:38], border=1)
        pdf.cell(col_w[1], 7, job["tech_name"], border=1)
        pdf.cell(col_w[2], 7, f"Rs {int(job['cost']):,}", border=1)
        pdf.cell(col_w[3], 7, PAYMENT_DISPLAY.get(job["payment"], job["payment"]), border=1)
        pdf.ln()
        if job.get("note"):
            pdf.set_font("Helvetica", "I", 8)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(10)
            pdf.cell(0, 5, f"  Note: {job['note']}", new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", "", 10)

    # ── Total ─────────────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_fill_color(245, 245, 245)
    total_x = col_w[0] + col_w[1]
    pdf.cell(total_x, 8, "Total", border=1, fill=True)
    pdf.cell(col_w[2], 8, f"Rs {int(summary['total']):,}", border=1, fill=True)
    pdf.cell(col_w[3], 8, "", border=1, fill=True)
    pdf.ln(12)

    # ── Footer ────────────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(140, 140, 140)
    pdf.cell(0, 6, f"Thank you for visiting {SALON_NAME}!", align="C")

    return bytes(pdf.output())


def generate_whatsapp_text(summary: dict) -> str:
    lines = [
        f"*{SALON_NAME} — Invoice #{summary['visit_id']}*",
        f"Date: {summary['visit_date']}",
        f"Customer: {summary['customer_name']}",
        "",
        "*Services:*",
    ]
    for job in summary["jobs"]:
        payment = PAYMENT_DISPLAY.get(job["payment"], job["payment"])
        line = f"  • {job['service']} — Rs {int(job['cost']):,} ({payment})"
        if job.get("note"):
            line += f" _{job['note']}_"
        lines.append(line)

    lines += [
        "",
        f"*Total: Rs {int(summary['total']):,}*",
        "",
        f"Thank you for visiting {SALON_NAME}! \U0001f485",
    ]
    return "\n".join(lines)


def whatsapp_link(phone: str, text: str) -> str:
    cleaned = "".join(c for c in phone if c.isdigit())
    if len(cleaned) == 10:
        cleaned = "91" + cleaned
    return f"https://wa.me/{cleaned}?text={urllib.parse.quote(text)}"
