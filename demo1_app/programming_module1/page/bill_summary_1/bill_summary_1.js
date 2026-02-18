frappe.pages['bill-summary-1'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Bill Split',
		single_column: true
	});
}