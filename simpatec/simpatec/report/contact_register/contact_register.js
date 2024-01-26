// Copyright (c) 2024, Phamos GmbH and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.provide("contact_register")
frappe.query_reports["Contact Register"] = {
	"filters": [

	],

	onload: async function (report) {
		$(".custom-actions").hide();
		$(".standard-actions").hide();
		make_filter_list();
		// $(".page-actions").append(`<button class='btn btn-default btn-sm ellipsis contact-set-route' onclick='route_to_contact_set()'>Goto Contact Set</button>`);
		// route_to_contact_set = function () {
		// 	frappe.set_route("List", "Contact Set");
		// 	$(".contact-set-route").hide();
		// }

		contact_register.open_dialog = function (contact, contact_row) {
			let d = new frappe.ui.Dialog({
				title: "Enter details",
				fields: [
					{
						label: "Contact Set",
						fieldname: "contact_set",
						fieldtype: "Link",
						options: "Contact Set"
					}
				],
				primary_action_label: "Create",
				primary_action() {
					var data = d.get_values();
					frappe.call({
						method: "simpatec.simpatec.report.contact_register.contact_register.update_row_in_contact_set",
						args: {
							contact: contact,
							contact_row: contact_row,
							contact_set: data.contact_set
						},
						callback: function (r) {
							report.refresh()
							// frappe.msgprint(`A new ProMa Checklist was created: <a href="/app/proma-checklist/${r.message}">${r.message}</a>`, "Success")
						}
					})

					d.hide();
				}
			});
			d.show();
		}
	}
};


var make_filter_list = function () {
	var filter_list_wrapper = $(".page-actions")
	$(`<div class="filter-selector">
		<button class="btn btn-default btn-sm filter-button">
			<span class="filter-icon">
				${frappe.utils.icon('filter')}
			</span>
			<span class="button-label hidden-xs">
				${__("Filter")}
			<span>
		</button>
	</div>`
	).appendTo(filter_list_wrapper);

	var filter_button = filter_list_wrapper.find('.filter-button');
	this.filter_list = new frappe.ui.FilterGroup({
		// base_list: this.list_view,
		parent: filter_list_wrapper,
		doctype: "Contact",
		filter_button: filter_button,
		default_filters: [],
		// on_change: () => {},
		on_change: () => {
			var filters = this.filter_list.get_filters();
			frappe.call({
				method: "simpatec.simpatec.report.contact_register.contact_register.execute",
				args: {
					filters: filters
				},
				freeze: true,
				freeze_message: "Loading data..."
			}).then(r => {
				if (r.message){
					$(".report-wrapper").next().hide()
				}
				var data = {
					columns: r.message[0],
					result: r.message[1]
				}
				frappe.query_report.prepare_report_data(data);
				frappe.query_report.render_datatable()
			})
		},
	});
}