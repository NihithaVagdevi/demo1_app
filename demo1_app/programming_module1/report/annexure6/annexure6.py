import frappe
from frappe import _


def execute(filters=None):
    if not filters:
        filters = {}

    if not filters.get("fiscal_year"):
        frappe.throw(_("Fiscal Year is mandatory"))

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():
    return [
        {"label": _("S.No"), "fieldname": "sno", "fieldtype": "Int", "width": 60},
        {"label": _("Particulars"), "fieldname": "particulars", "fieldtype": "Data", "width": 420},
        {"label": _("IGST"), "fieldname": "igst", "fieldtype": "Currency", "width": 150},
        {"label": _("CGST"), "fieldname": "cgst", "fieldtype": "Currency", "width": 150},
        {"label": _("SGST"), "fieldname": "sgst", "fieldtype": "Currency", "width": 150},
        {"label": _("Total"), "fieldname": "total", "fieldtype": "Currency", "width": 170},
    ]


def get_itc_accounts(company):
    accounts = frappe.db.sql(
        """
        SELECT name
        FROM `tabAccount`
        WHERE company = %s
        AND is_group = 0
        AND (
            name LIKE '%%IGST%%'
            OR name LIKE '%%CGST%%'
            OR name LIKE '%%SGST%%'
        )
        """,
        (company,),
        as_dict=True,
    )

    igst, cgst, sgst = [], [], []

    for a in accounts:
        if "IGST" in a.name:
            igst.append(a.name)
        elif "CGST" in a.name:
            cgst.append(a.name)
        elif "SGST" in a.name:
            sgst.append(a.name)

    return igst, cgst, sgst


def get_sum(company, igst_acc, cgst_acc, sgst_acc, condition, params, mode):

    def clause(lst):
        return ",".join(["%s"] * len(lst)) if lst else "''"

    if mode == "debit":
        field = "debit"
    elif mode == "credit":
        field = "credit"
    else:
        field = "(debit - credit)"

    query = f"""
        SELECT
            SUM(CASE WHEN account IN ({clause(igst_acc)}) THEN {field} ELSE 0 END) AS igst,
            SUM(CASE WHEN account IN ({clause(cgst_acc)}) THEN {field} ELSE 0 END) AS cgst,
            SUM(CASE WHEN account IN ({clause(sgst_acc)}) THEN {field} ELSE 0 END) AS sgst
        FROM `tabGL Entry`
        WHERE docstatus = 1
        AND company = %s
        AND {condition}
    """

    values = []
    values.extend(igst_acc)
    values.extend(cgst_acc)
    values.extend(sgst_acc)
    values.append(company)
    values.extend(params)

    res = frappe.db.sql(query, values, as_dict=True)[0]

    return {
        "igst": res.igst or 0,
        "cgst": res.cgst or 0,
        "sgst": res.sgst or 0,
    }

def get_data(filters):

    fy = frappe.get_doc("Fiscal Year", filters["fiscal_year"])
    from_date = fy.year_start_date
    to_date = fy.year_end_date

    if filters.get("company") and filters["company"] != "All":
        companies = [filters["company"]]
    else:
        companies = frappe.db.get_all("Company", pluck="name")

    opening_total = {"igst": 0, "cgst": 0, "sgst": 0}
    availed_total = {"igst": 0, "cgst": 0, "sgst": 0}
    utilised_total = {"igst": 0, "cgst": 0, "sgst": 0}

    for company in companies:
        igst_acc, cgst_acc, sgst_acc = get_itc_accounts(company)

        if not (igst_acc or cgst_acc or sgst_acc):
            continue

        opening = get_sum(
            company,
            igst_acc, cgst_acc, sgst_acc,
            "posting_date < %s",
            [from_date],
            mode="net"
        )

        availed = get_sum(
            company,
            igst_acc, cgst_acc, sgst_acc,
            "posting_date BETWEEN %s AND %s",
            [from_date, to_date],
            mode="debit"
        )

        utilised = get_sum(
            company,
            igst_acc, cgst_acc, sgst_acc,
            "posting_date BETWEEN %s AND %s",
            [from_date, to_date],
            mode="credit"
        )

        for k in ["igst", "cgst", "sgst"]:
            opening_total[k] += opening[k]
            availed_total[k] += availed[k]
            utilised_total[k] += utilised[k]

    closing_total = {
        "igst": opening_total["igst"] + availed_total["igst"] - utilised_total["igst"],
        "cgst": opening_total["cgst"] + availed_total["cgst"] - utilised_total["cgst"],
        "sgst": opening_total["sgst"] + availed_total["sgst"] - utilised_total["sgst"],
    }

    data = [
        {
            "sno": 1,
            "particulars": "Balance representing credits at the beginning of the year",
            "igst": opening_total["igst"],
            "cgst": opening_total["cgst"],
            "sgst": opening_total["sgst"],
            "total": sum(opening_total.values()),
        },
        {
            "sno": 2,
            "particulars": "Inputs available during the year",
            "igst": availed_total["igst"],
            "cgst": availed_total["cgst"],
            "sgst": availed_total["sgst"],
            "total": sum(availed_total.values()),
        },
        {
            "sno": 3,
            "particulars": "Less: Amount of credit utilised during the year",
            "igst": utilised_total["igst"],
            "cgst": utilised_total["cgst"],
            "sgst": utilised_total["sgst"],
            "total": sum(utilised_total.values()),
        },
        {
            "sno": 4,
            "particulars": "Balance representing outstanding amount at the end of the year",
            "igst": closing_total["igst"],
            "cgst": closing_total["cgst"],
            "sgst": closing_total["sgst"],
            "total": sum(closing_total.values()),
        },
    ]

    return data
