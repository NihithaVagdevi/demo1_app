import frappe
from frappe import _
import re


# =========================================================
# ANNEXURE 11 – Clause 34(a) Form 3CD
# =========================================================

def execute(filters=None):

    if not filters:
        filters = {}

    if not filters.get("fiscal_year"):
        frappe.throw("Fiscal Year is mandatory")

    columns = get_columns()
    data = get_data(filters)

    return columns, data


# =========================================================
# COLUMNS
# =========================================================

def get_columns():
    return [

        {
            "label": _("Tax Deduction And Collection Account Number (TAN)"),
            "fieldname": "tan",
            "fieldtype": "Data",
            "width": 160
        },
        {
            "label": _("Section"),
            "fieldname": "section",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": _("Nature of Payment"),
            "fieldname": "nature_of_payment",
            "fieldtype": "Dynamic Link",
            "options": "reference_doctype",
            "width": 220
        },
        {
            "label": _("Total Amount of Payment or Receipt of the Nature Specified in Column (3)"),
            "fieldname": "total_paid",
            "fieldtype": "Currency",
            "width": 220
        },
        {
            "label": _("Total Amount on Which Tax Was Required to be Deducted or Collected Out of (4)"),
            "fieldname": "tds_base",
            "fieldtype": "Currency",
            "width": 220
        },
        {
            "label": _("Total Amount on Which Tax Was Required to be Deducted or Collected at Specified Rate Out of (5)"),
            "fieldname": "specified_rate_base",
            "fieldtype": "Currency",
            "width": 240
        },
        {
            "label": _("Amount of Tax Deducted or Collected Out of (6)"),
            "fieldname": "tds_amount",
            "fieldtype": "Currency",
            "width": 200
        },
        {
            "label": _("Total Amount on Which Tax Was Deducted or Collected at Less than Specified Rate Out of (5)"),
            "fieldname": "lower_rate_base",
            "fieldtype": "Currency",
            "width": 240
        },
        {
            "label": _("Amount of Tax Deducted or Collected out on (5)"),
            "fieldname": "lower_rate_tax",
            "fieldtype": "Currency",
            "width": 200
        },
        {
            "label": _("Amount of Tax Deducted or Collected Not Deposited To The Credit Of The Central Government Out of (6) and (8)"),
            "fieldname": "not_deposited",
            "fieldtype": "Currency",
            "width": 260
        }
    ]


# =========================================================
# DATA LOGIC – PURCHASE INVOICE TDS ONLY
# =========================================================

def get_data(filters):

    fy = frappe.get_doc("Fiscal Year", filters["fiscal_year"])
    from_date = fy.year_start_date
    to_date = fy.year_end_date

    if filters.get("company") and filters.get("company") != "All":
        companies = [filters.get("company")]
    else:
        companies = frappe.get_all("Company", pluck="name")

    final_data = []

    for company in companies:

        tan = frappe.db.get_value("Company", company, "tax_id") or ""

        tds_rows = frappe.db.sql("""
            SELECT
                gle.account,
                gle.voucher_no,
                SUM(gle.credit) as tds_amount
            FROM `tabGL Entry` gle
            WHERE gle.docstatus = 1
            AND gle.company = %s
            AND gle.posting_date BETWEEN %s AND %s
            AND gle.voucher_type = 'Purchase Invoice'
            AND gle.credit > 0
            AND gle.account LIKE '%%TDS%%'
            GROUP BY gle.account, gle.voucher_no
        """, (company, from_date, to_date), as_dict=True)

        for row in tds_rows:

            section = extract_section(row.account)

            if not section:
                continue

            base_amount = frappe.db.sql("""
                SELECT SUM(debit)
                FROM `tabGL Entry`
                WHERE voucher_no = %s
                AND voucher_type = 'Purchase Invoice'
                AND company = %s
                AND debit > 0
                AND account NOT LIKE '%%TDS%%'
            """, (row.voucher_no, company))[0][0] or 0

            final_data.append({
                "tan": tan,
                "section": section,
                "nature_of_payment": row.account,   # Account name
                "reference_doctype": "Account",    # 🔥 This makes it Dynamic Link
                "total_paid": base_amount,
                "tds_base": base_amount,
                "specified_rate_base": base_amount,
                "tds_amount": row.tds_amount or 0,
                "lower_rate_base": 0,
                "lower_rate_tax": 0,
                "not_deposited": 0,
            })

    return final_data



def extract_section(account_name):

    match = re.search(r'(\d{3}[A-Z]?)', account_name)

    if match:
        return match.group(1)

    return ""
