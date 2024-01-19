// Copyright (c) 2024, Phamos GmbH and contributors
// For license information, please see license.txt
/* eslint-disable */
frappe.provide("contact_set_control_panel")

frappe.query_reports["Contact Set Action Panel"] = {
	"filters": [
		{
			"fieldname":"contact_set",
			"label": __("Contact Set"),
			"fieldtype": "Link",
			"options": "Contact Set",
			"reqd": 1
		},
	],

	onload: async function (report) {
		$(".custom-actions").hide();
		$(".standard-actions").hide();

		contact_set_control_panel.open_dialog = function (row) {


			let contact_set = (row["contact_set"] === 'null') ? null : row["contact_set"];
			let contact_set_row = (row["contact_set_row"] === 'null') ? null : row["contact_set_row"];
			let notes = (row["notes"] === 'null') ? null : row["notes"];
			let status = (row["status"] === 'null') ? null : row["status"];
			let emails = (row["emails"] === 'null') ? null : row["emails"];
			let phone_nos = (row["phone_nos"] === 'null') ? null : row["phone_nos"];
			let first_name = (row["first_name"] === 'null') ? null : row["first_name"];
			let last_name = (row["last_name"] === 'null') ? null : row["last_name"];
			let contact_name = (first_name && last_name) ? `${first_name} ${last_name}` : first_name;

			var getContactInfoHtml = function (contactInfo, field, linkType, label) {
				let contactInfoHtmlOutput = '';
				let html_segment = "<span></span>"

				let linkPrefix = (linkType === 'email') ? 'mailto:' : 'tel:';			
				contactInfo.forEach(infoObj => {
					let value = infoObj[field.toLowerCase()];
					let link = `${linkPrefix}${value}`;					
					let divElement = `<p><a href="${link}">${value}</a></p>`;			
					contactInfoHtmlOutput += divElement;
				});

				if (contactInfoHtmlOutput) {
					html_segment =  `<div class="form-group">
						<div class="clearfix">
							<label class="control-label" style="padding-right: 0px;">${label}</label>
							<span class="help"></span>
						</div>
						<div class="like-disabled-input">${contactInfoHtmlOutput}</div>
					</div>`
				}
				return html_segment
			}

			let d = new frappe.ui.Dialog({
				title: "Take Action",
				// size: "large",
				 size: "extra-large",
				fields: [
					{
						label: "Contact Name",
						fieldname: "contact_name",
						fieldtype: "HTML",
						options: `<h3>${contact_name}</h3>`,
						read_only: 1
					},
					{
						label: "Email Address",
						fieldname: "email_address",
						fieldtype: "HTML",
						options: getContactInfoHtml(emails, 'email_id', 'email', "Emails"),
						hidden: 1
					},
					{
						label: "Phone Nos",
						fieldname: "phone_nos",
						fieldtype: "HTML",
						options: getContactInfoHtml(phone_nos, 'phone', 'phone', "Phone Nos")
					},
					{
						fieldname: "colbreak1234",
						fieldtype: "Column Break"
					},
					{
						label: "Status",
						fieldname: "status",
						fieldtype: "Select",
						options: "\nNew\nIn Work\nRejected\nOpportunity",
						default: status
					},
					{
						label: "Notes",
						fieldname: "notes",
						fieldtype: "Small Text",
						default: notes
					},

				],
				primary_action_label: "Update",
				primary_action() {
					var data = d.get_values();
					console.log(emails)
					frappe.call({
						method: "simpatec.simpatec.report.contact_set_action_panel.contact_set_action_panel.update_row_in_contact_set",
						args: {
							contact_set: contact_set,
							contact_set_row: contact_set_row,
							data: data
						},
						callback: function (r) {
							report.refresh();
						}
					})

					d.hide();
				}
			});
			d.show();
		}
	}
};
