import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class Payment(Document):

    def autoname(self):
        self.name = make_autoname("PAY-.#####")

    def validate(self):
        if not self.amount_paid or self.amount_paid <= 0:
            frappe.throw("Paid Amount must be greater than zero")

        if not self.debt:
            frappe.throw("Debt is required")

        debt = frappe.get_doc("Debt", self.debt)

        if self.amount_paid > debt.remaining_amount:
            frappe.throw("Paid Amount cannot exceed Due Amount")

        self.from_user = debt.from_user
        self.to_user = debt.to_user

        self.due_amount = debt.remaining_amount

    def on_submit(self):
        debt = frappe.get_doc("Debt", self.debt)

        debt.paid_amount = (debt.paid_amount or 0) + self.amount_paid
        debt.remaining_amount = debt.original_amount - debt.paid_amount

        if debt.remaining_amount <= 0:
            debt.remaining_amount = 0
            debt.status = "Paid"
        else:
            debt.status = "Partial"

        debt.save(ignore_permissions=True)
