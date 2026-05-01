SERVICES = [
    "Nails",
    "Eye Lash",
    "Eye Brows",
    "Lips",
    "Manicure Pedicure",
]

PAYMENT_METHODS = ["Cash", "UPI/QR"]

# Internal DB values (must match CHECK constraint in schema)
PAYMENT_METHOD_MAP = {
    "Cash": "CASH",
    "UPI/QR": "UPI",
}
