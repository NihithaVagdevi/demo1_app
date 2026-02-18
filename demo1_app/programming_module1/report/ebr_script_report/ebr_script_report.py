import frappe

def execute(filters=None):

    columns = [

        {
            "label": "Journal Entry",
            "fieldname": "je_name",
            "fieldtype": "Link",
            "options": "Journal Entry",
            "width": 150
        },
        {
            "label": "Posting Date",
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 110
        },
        {
            "label": "Company",
            "fieldname": "company",
            "fieldtype": "Link",
            "options": "Company",
            "width": 140
        },
        {
            "label": "Buyer Name",
            "fieldname": "customer",
            "fieldtype": "Data",
            "width": 160
        },
        {
            "label": "BL Date",
            "fieldname": "custom_bl_date",
            "fieldtype": "Date",
            "width": 110
        },
        {
            "label": "Discount Date",
            "fieldname": "custom_discount_date",
            "fieldtype": "Date",
            "width": 110
        },
        {
            "label": "Bill Number",
            "fieldname": "custom_bill_number",
            "fieldtype": "Data",
            "width": 140
        },
        {
            "label": "No of Days",
            "fieldname": "custom_no_of_days",
            "fieldtype": "Int",
            "width": 90
        },
        {
            "label": "EBR Due Date",
            "fieldname": "custom_ebr_due_date",
            "fieldtype": "Date",
            "width": 120
        },

        # Hidden currency field (forces $)
        {
            "fieldname": "currency",
            "fieldtype": "Data",
            "hidden": 1
        },

        {
            "label": "EBR Amount",
            "fieldname": "ebr_amount",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 130
        },

        {
            "label": "Sales Invoice",
            "fieldname": "sales_invoice",
            "fieldtype": "Link",
            "options": "Sales Invoice",
            "width": 150
        }
    ]

    data = frappe.db.sql("""
        SELECT
            je.name AS je_name,
            je.posting_date,
            je.company,
            si.customer,
            je.custom_bl_date,
            je.custom_discount_date,
            je.custom_bill_number,
            je.custom_no_of_days,
            je.custom_ebr_due_date,
            je.custom_sales_invoice_ref_no AS sales_invoice,

            'USD' AS currency,

            (
                SELECT SUM(jed.credit_in_account_currency)
                FROM `tabJournal Entry Account` jed
                WHERE jed.parent = je.name
                AND jed.account LIKE '%%EBR%%'
            ) AS ebr_amount

        FROM `tabJournal Entry` je

        LEFT JOIN `tabSales Invoice` si
            ON si.name = je.custom_sales_invoice_ref_no

        WHERE
            je.docstatus = 1
            AND je.custom_ebr_due_date IS NOT NULL

        ORDER BY je.posting_date DESC

    """, as_dict=True)

    return columns, data
