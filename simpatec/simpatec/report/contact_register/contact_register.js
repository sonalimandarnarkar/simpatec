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
		// $(".page-actions").append('<button class="btn btn-default btn-sm ellipsis" ><a href="/app/contact-set" target="_blank">Goto Contact Set</button>')

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
