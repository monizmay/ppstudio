SERVICES = [
    "Nails",
    "Eye Lash",
    "Eye Brows",
    "Lips",
    "Manicure Pedicure",
    "Others (please mention in Job Notes)",
]

PAYMENT_METHODS = ["Cash", "UPI/QR"]

# Internal DB values (must match CHECK constraint in schema)
PAYMENT_METHOD_MAP = {
    "Cash": "CASH",
    "UPI/QR": "UPI",
}
