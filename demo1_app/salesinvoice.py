import frappe

def validate_sales_invoice(doc, method):
    if doc.grand_total < 500:
        frappe.throw("Sales Invoice total must be at least 500")
