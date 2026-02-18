frappe.pages['demo_1'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Programming ',
		single_column: true
	});
}