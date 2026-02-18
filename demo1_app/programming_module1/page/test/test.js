frappe.pages['test'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Test',
		single_column: true
	});
	page.set_title('Hello')

	page.set_indicator('Done', 'green');

	let $btn=page.set_primary_action('New', ()=>frappe.msgprint('New Button Clicked'));

	let $btOne=page.set_secondary_action('Refresh', ()=>frappe.msgprint('Refresh Button Clicked'));

	page.add_menu_item('Send Email', ()=>frappe.msgprint('Send Email Clicked'));

	page.add_action_item('Delete', ()=>frappe.msgprint('Delete Clicked'));

	let field=page.add_field({
		label:'Status',
		fieldname:'status',
		fieldtype:'Select',
		options:['Open', 'Closed','Cancelled'],
		change(){
			frappe.msgprint(`Status changed to ${this.value}`);
		}
	});
	//$(frappe.render_template("test", {})).appendTo(page.body);

	$(frappe.render_template("test", {
		data:"This is demo page content"
	})).appendTo(page.body);
}