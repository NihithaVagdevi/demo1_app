import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class Debt(Document):

    def autoname(self):
        self.name = make_autoname("DEB-.#####")

    def validate(self):
        original = self.original_amount or 0
        paid = self.paid_amount or 0

        
        if paid > original:
            frappe.throw("Paid amount cannot be greater than original amount")

        remaining = original - paid
        self.remaining_amount = remaining
        self.remaining_amount_db = remaining

        if remaining == 0:
            self.status = "Paid"
        elif paid > 0:
            self.status = "Partial"
        else:
            self.status = "Unpaid"
