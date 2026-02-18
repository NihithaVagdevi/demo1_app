// Copyright (c) 2026, Demo and contributors
// For license information, please see license.txt

frappe.query_reports["Payer Summary"] = {
    filters: [
        {
            fieldname: "to_user",
            label: "Payer",
            fieldtype: "Link",
            options: "User",
            reqd: 0
        }
    ]
};
