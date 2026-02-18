import frappe
from frappe.utils import add_days

def execute(filters=None):

    columns = [
        {"label": "Journal Entry", "fieldname": "je_name",
         "fieldtype": "Link", "options": "Journal Entry", "width": 160},

        {"label": "Company", "fieldname": "company",
         "fieldtype": "Link", "options": "Company", "width": 150},

        {"label": "PCFC Reference", "fieldname": "pcfc_ref",
         "fieldtype": "Data", "width": 150},

        {"label": "Posting Date", "fieldname": "posting_date",
         "fieldtype": "Date", "width": 120},

        {"label": "Days", "fieldname": "days",
         "fieldtype": "Int", "width": 100},

        {"label": "PCFC Due Date", "fieldname": "due_date",
         "fieldtype": "Date", "width": 120},

        {"label": "Original Amount ($)", "fieldname": "original_amount",
         "fieldtype": "Float", "width": 150},

        {"label": "Utilized Amount ($)", "fieldname": "utilized_amount",
         "fieldtype": "Float", "width": 150},

        {"label": "Balance Amount ($)", "fieldname": "balance_amount",
         "fieldtype": "Float", "width": 150},
    ]

    # Step 1: Get ONLY the Loan JE (credit entry in PCFC account)
    loan_entry = frappe.db.sql("""
        SELECT
            je.name AS je_name,
            je.company,
            je.posting_date,
            je.custom_pcfc_reference_number AS pcfc_ref,
            je.custom_days AS days,
            gle.credit_in_account_currency AS original_amount
        FROM `tabGL Entry` gle
        JOIN `tabJournal Entry` je
            ON gle.voucher_no = je.name
        WHERE
            gle.account = 'ICICI PCFC Account - SPLCGD'
            AND gle.credit_in_account_currency > 0
            AND gle.docstatus = 1
        LIMIT 1
    """, as_dict=True)

    if not loan_entry:
        return columns, []

    row = loan_entry[0]
    pcfc_ref = row.pcfc_ref

    # Step 2: Get Utilized Amount (Debit side)
    utilized = frappe.db.sql("""
        SELECT
            SUM(gle.debit_in_account_currency) AS utilized_amount
        FROM `tabGL Entry` gle
        JOIN `tabJournal Entry` je
            ON gle.voucher_no = je.name
        WHERE
            gle.account = 'ICICI PCFC Account - SPLCGD'
            AND gle.debit_in_account_currency > 0
            AND je.custom_pcfc_reference_number = %s
            AND gle.docstatus = 1
    """, (pcfc_ref,), as_dict=True)[0]

    utilized_amount = utilized.utilized_amount or 0
    original_amount = row.original_amount or 0
    balance_amount = original_amount - utilized_amount

    days = row.days or 0
    due_date = add_days(row.posting_date, days) if days else row.posting_date

    data = [{
        "je_name": row.je_name,
        "company": row.company,
        "pcfc_ref": pcfc_ref,
        "posting_date": row.posting_date,
        "days": days,
        "due_date": due_date,
        "original_amount": original_amount,
        "utilized_amount": utilized_amount,
        "balance_amount": balance_amount
    }]

    return columns, data
