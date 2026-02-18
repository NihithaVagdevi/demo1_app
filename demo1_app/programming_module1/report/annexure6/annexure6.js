frappe.query_reports["Annexure6"] = {
    filters: [
        {
            fieldname: "fiscal_year",
            label: __("Fiscal Year"),
            fieldtype: "Link",
            options: "Fiscal Year",
            reqd: 1
        },
        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Select",
            options: ["All"],
            default: "All"
        }
    ],

    onload: function (report) {
        // Fetch companies dynamically and add to dropdown
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Company",
                fields: ["name"],
                limit_page_length: 100
            },
            callback: function (r) {
                if (r.message) {
                    let company_filter = report.get_filter("company");
                    let options = ["All"];

                    r.message.forEach(c => {
                        options.push(c.name);
                    });

                    company_filter.df.options = options;
                    company_filter.refresh();
                }
            }
        });
    }
};
