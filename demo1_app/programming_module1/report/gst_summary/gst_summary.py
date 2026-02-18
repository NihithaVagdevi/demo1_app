import frappe


def execute(filters=None):
    filters = filters or {}
    validate_filters(filters)

    group_by = filters.get("group_by", "Party")
    party_type = filters.get("party_type")

    columns = get_columns(group_by, party_type)
    data = get_data(filters, group_by, party_type)

    return columns, data


def validate_filters(filters):
    if not filters.get("from_date") or not filters.get("to_date"):
        frappe.throw("From Date and To Date are required")
    if not filters.get("party_type"):
        frappe.throw("Party Type is required")



def get_columns(group_by, party_type):
    columns = [
        {"label": "Date", "fieldname": "date", "fieldtype": "Date", "width": 110},
        {"label": "Invoice No", "fieldname": "invoice_no", "width": 150},
        {
            "label": "Party",
            "fieldname": "party",
            "fieldtype": "Dynamic Link",
            "options": "party_type",
            "width": 200,
        },
        {"label": "Party Type", "fieldname": "party_type", "width": 110},
        {"label": "HSN", "fieldname": "hsn", "width": 120},
        {"label": "GSTIN", "fieldname": "gstin", "width": 150},
        {"label": "GST Category", "fieldname": "gst_category", "width": 150},
        {"label": "GST / Non-GST", "fieldname": "gst_type", "width": 120},
    ]

    if group_by == "Voucher":
        columns.append({
            "label": "Voucher No",
            "fieldname": "voucher_no",
            "fieldtype": "Dynamic Link",
            "options": "voucher_type",
            "width": 180,
        })

    columns += [
        {"label": "Taxable Amount", "fieldname": "taxable_amount", "fieldtype": "Currency", "width": 130},
        {"label": "CGST", "fieldname": "cgst_amount", "fieldtype": "Currency", "width": 120},
        {"label": "SGST", "fieldname": "sgst_amount", "fieldtype": "Currency", "width": 120},
        {"label": "IGST", "fieldname": "igst_amount", "fieldtype": "Currency", "width": 120},
        {"label": "GST Amount", "fieldname": "gst_amount", "fieldtype": "Currency", "width": 130},
        {"label": "Total Amount", "fieldname": "total_amount", "fieldtype": "Currency", "width": 150},
    ]

    return columns



def get_data(filters, group_by, party_type):
    data = []

    if party_type in ("Supplier", "Both"):
        data += get_purchase_data(filters, group_by)

    if party_type in ("Customer", "Both"):
        data += get_sales_data(filters, group_by)

    return data



def get_purchase_data(filters, group_by):
    params = {
        "from_date": filters.from_date,
        "to_date": filters.to_date,
    }

    group_clause = "pi.name"
    voucher_select = ", 'Purchase Invoice' AS voucher_type, pi.name AS voucher_no"

    query = f"""
        SELECT
            pi.posting_date AS date,
            pi.name AS invoice_no,
            pi.supplier AS party,
            'Supplier' AS party_type,
            sup.gstin AS gstin,
            pi.tax_category AS gst_category,
            GROUP_CONCAT(DISTINCT pii.gst_hsn_code) AS hsn,

            SUM(pii.base_net_amount) AS taxable_amount,

            SUM(CASE WHEN pitc.account_head LIKE '%%CGST%%' THEN pitc.base_tax_amount ELSE 0 END) AS cgst_amount,
            SUM(CASE WHEN pitc.account_head LIKE '%%SGST%%' THEN pitc.base_tax_amount ELSE 0 END) AS sgst_amount,
            SUM(CASE WHEN pitc.account_head LIKE '%%IGST%%' THEN pitc.base_tax_amount ELSE 0 END) AS igst_amount

        FROM `tabPurchase Invoice` pi
        JOIN `tabPurchase Invoice Item` pii ON pii.parent = pi.name
        JOIN `tabSupplier` sup ON sup.name = pi.supplier
        LEFT JOIN `tabPurchase Taxes and Charges` pitc ON pitc.parent = pi.name

        WHERE
            pi.docstatus = 1
            AND pi.posting_date BETWEEN %(from_date)s AND %(to_date)s

        GROUP BY {group_clause}
    """

    return process_rows(query, params, filters, group_by)



def get_sales_data(filters, group_by):
    params = {
        "from_date": filters.from_date,
        "to_date": filters.to_date,
    }

    group_clause = "si.name"
    voucher_select = ", 'Sales Invoice' AS voucher_type, si.name AS voucher_no"

    query = f"""
        SELECT
            si.posting_date AS date,
            si.name AS invoice_no,
            si.customer AS party,
            'Customer' AS party_type,
            cust.gstin AS gstin,
            si.tax_category AS gst_category,
            GROUP_CONCAT(DISTINCT sii.gst_hsn_code) AS hsn,

            SUM(sii.base_net_amount) AS taxable_amount,

            SUM(CASE WHEN sitc.account_head LIKE '%%CGST%%' THEN sitc.base_tax_amount ELSE 0 END) AS cgst_amount,
            SUM(CASE WHEN sitc.account_head LIKE '%%SGST%%' THEN sitc.base_tax_amount ELSE 0 END) AS sgst_amount,
            SUM(CASE WHEN sitc.account_head LIKE '%%IGST%%' THEN sitc.base_tax_amount ELSE 0 END) AS igst_amount

        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        JOIN `tabCustomer` cust ON cust.name = si.customer
        LEFT JOIN `tabSales Taxes and Charges` sitc ON sitc.parent = si.name

        WHERE
            si.docstatus = 1
            AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s

        GROUP BY {group_clause}
    """

    return process_rows(query, params, filters, group_by)



def process_rows(query, params, filters, group_by):
    rows = frappe.db.sql(query, params, as_dict=True)
    data = []

    for r in rows:
        cgst = r.cgst_amount or 0
        sgst = r.sgst_amount or 0
        igst = r.igst_amount or 0

        gst_amount = cgst + sgst + igst
        taxable = r.taxable_amount or 0

        gst_type = "GST" if gst_amount > 0 else "Non-GST"
        filter_gst_type = filters.get("gst_type", "All")
        if filter_gst_type != "All" and filter_gst_type != gst_type:
            continue

        row = {
            "date": r.date,
            "invoice_no": r.invoice_no,
            "party": r.party,
            "party_type": r.party_type,
            "hsn": r.hsn,
            "gstin": r.gstin,
            "gst_category": r.gst_category,
            "gst_type": gst_type,
            "taxable_amount": taxable,
            "cgst_amount": cgst,
            "sgst_amount": sgst,
            "igst_amount": igst,
            "gst_amount": gst_amount,
            "total_amount": taxable + gst_amount,
        }

        if group_by == "Voucher":
            row["voucher_type"] = r.voucher_type
            row["voucher_no"] = r.voucher_no

        data.append(row)

    return data
