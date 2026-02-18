// Copyright (c) 2026, Demo and contributors
// For license information, please see license.txt

frappe.query_reports["Server side scripting Script Report"] = {
	"filters": [
		{
			"filedname":"name",
			"label":__("Server Side Scripting Name"),
			"fieldtype":"Link",
			"options":"Server Side Scripting"
			
		},
		{
			"filedname":"dob",
			"label":__("DOB"),
			"fieldtype":"Date"
		},
		{
			"filedname":"age",
			"label":__("Age"),
			"fieldtype":"Data"
		}

	]
};
