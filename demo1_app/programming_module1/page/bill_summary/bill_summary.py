import frappe

@frappe.whitelist()
def get_summary():
    bills = frappe.get_all("Expense", fields=["total_amount"])
    total = sum(b.total_amount for b in bills)

    return {
        "count": len(bills),
        "total": total
    }
