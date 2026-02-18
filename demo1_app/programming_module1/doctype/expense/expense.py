import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class Expense(Document):

    def autoname(self):
        self.name = make_autoname("EXP-.#####")

    def on_submit(self):
        if self.debts_created:
            return

        if not self.participants:
            frappe.throw("Participants are required")

        if not self.total_amount or not self.paid_by:
            frappe.throw("Total Amount and Paid By are required")

        participants = self.participants
        total = self.total_amount
        paid_by = self.paid_by

        count = len(participants)
        if count == 0:
            return
        share = round(total / count, 2)

        for row in participants:
            if row.user == paid_by:
                continue

            debt = frappe.new_doc("Debt")
            debt.from_user = row.user      
            debt.to_user = paid_by         
            debt.original_amount = share
            debt.paid_amount = 0
            debt.remaining_amount = share
            debt.status = "Unpaid"
            debt.expense = self.name
            debt.insert(ignore_permissions=True)

        # Mark as processed
        self.db_set("debts_created", 1)
