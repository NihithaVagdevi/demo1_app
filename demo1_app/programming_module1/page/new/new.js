frappe.pages['new'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Hello',
		single_column: true
	});

	// Add a button
	page.add_inner_button(__('Show Message'), function() {
		// Show popup message
		frappe.msgprint(__('Hello! This is a popup message.'));
	});
	page.body.on('click', '#popup-btn', function () {
        frappe.msgprint("SPL ... Strategtic Planning & Lean ");
    });

 $(frappe.render_template("new", {})).appendTo(page.body);
};

