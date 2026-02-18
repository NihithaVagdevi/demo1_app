import frappe
from frappe.utils import getdate


def execute(filters=None):
    columns = get_columns()
    data = get_data()
    return columns, data


def get_columns():
    return [
        {
            "label": "Name of the Related Party",
            "fieldname": "related_party",
            "fieldtype": "Dynamic Link",
            "options": "party_type",
            "width": 220,
        },
        {
            "label": "PAN of the Related Party",
            "fieldname": "pan",
            "fieldtype": "Data",
            "width": 160,
        },
        {
            "label": "Relation",
            "fieldname": "relation",
            "fieldtype": "Data",
            "width": 160,
        },
        {
            "label": "Nature of Transaction",
            "fieldname": "nature_of_transaction",
            "fieldtype": "Data",
            "width": 180,
        },
        {
            "label": "Payment Made",
            "fieldname": "payment_made",
            "fieldtype": "Currency",
            "width": 150,
        },
    ]


def get_data():

    employees = frappe.get_all(
        "Employee",
        filters={"designation": "Director"},
        fields=["name", "employee_name", "pan_number", "designation"]
    )

    data = []

    for emp in employees:
        data.append({
            "related_party": emp.employee_name,   
            "party_type": "Employee",
            "pan": emp.pan_number,
            "relation": emp.designation,
            "nature_of_transaction": "Remuneration",
            "payment_made": 0
        })

    return data

