import frappe
import json

def execute(filters=None):
    # Normalize filters (Number Card sends list format)
    if isinstance(filters, str):
        filters = json.loads(filters)

    filter_dict = {}

    # Convert Query Report filter format to dict
    if isinstance(filters, list):
        # Example: [["Debt","to_user","=","a@gmail.com",false]]
        for f in filters:
            if len(f) >= 4:
                fieldname = f[1]
                value = f[3]
                filter_dict[fieldname] = value
    elif isinstance(filters, dict):
        filter_dict = filters

    conditions = ""
    values = {}

    if filter_dict.get("to_user"):
        conditions = "WHERE to_user = %(to_user)s"
        values["to_user"] = filter_dict["to_user"]

    columns = [
        {
            "label": "Payer",
            "fieldname": "to_user",
            "fieldtype": "Link",
            "options": "User",
            "width": 180,
        },
        {
            "label": "Split Amount",
            "fieldname": "total_amount",
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "label": "Paid Amount",
            "fieldname": "paid_amount",
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "label": "Remaining Amount",
            "fieldname": "remaining_amount",
            "fieldtype": "Currency",
            "width": 160,
        },
    ]

    data = frappe.db.sql(f"""
        SELECT
            to_user,
            SUM(original_amount) AS total_amount,
            SUM(paid_amount) AS paid_amount,
            SUM(remaining_amount) AS remaining_amount
        FROM `tabDebt`
        {conditions}
        GROUP BY to_user
    """, values=values, as_dict=True)

    return columns, data
