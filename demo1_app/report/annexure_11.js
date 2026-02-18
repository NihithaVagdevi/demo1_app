// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
 
frappe.query_reports["Annexure 11"] = {
 
    filters: [
 
        {
            fieldname: "fiscal_year",
            label: "Fiscal Year",
            fieldtype: "Link",
            options: "Fiscal Year",
            reqd: 1
        },
 
        {
            fieldname: "company",
            label: "Company",
            fieldtype: "Select",
            options: ["All"],
            default: "All"
        }
 
    ],
 
    onload: function(report) {
 
        // Load companies dynamically
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Company",
                fields: ["name"],
                limit_page_length: 500
            },
            callback: function(r) {
 
                if (r.message) {
 
                    let companies = ["All"];
 
                    r.message.forEach(function(c) {
                        companies.push(c.name);
                    });
 
                    report.set_filter_property("company", "options", companies);
                }
            }
        });
    }
};