// Copyright (c) 2026, Demo and contributors
// For license information, please see license.txt

frappe.query_reports["GST Summary"] = {
    filters: [
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            reqd: 1,
            default: frappe.datetime.month_start()
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            reqd: 1,
            default: frappe.datetime.month_end()
        },
        
        
        {
            fieldname: "party_type",
            label: __("Party Type"),
            fieldtype: "Select",
            options: ["Both", "Customer", "Supplier"],
            default: ""
        },
        
       
        {
            fieldname: "group_by",
            label: __("Group By"),
            fieldtype: "Select",
            options: ["Both", "Party", "Voucher"],
            default: "Party"
        },
        {
            fieldname: "gst_type",
            label: "GST / Non-GST",
            fieldtype: "Select",
            options: "All\nGST\nNon-GST",
            default: "All"
}
 
    ]
};