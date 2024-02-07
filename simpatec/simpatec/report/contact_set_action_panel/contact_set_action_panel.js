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
			"reqd": 1,
			"on_change": function(report) {
				set_contact_set_title();
				report.refresh();
			}
		}
	],

	onload: async function (report) {
		if ($('body[data-route="query-report/Contact Set Action Panel"]').length > 0) {
			let report_wrapper = $('body[data-route="query-report/Contact Set Action Panel"]');
			let page_action_wrapper = report_wrapper.find('div[id="page-query-report"]').find(".page-head-content").find(".page-actions");
			page_action_wrapper.html(`
			${get_default_standard_action_html()}
			<button class="btn btn-default btn-sm ellipsis contact-set-route" onclick="add_contact_to_contact_set()">Add Contact</button>`);
		}

		set_contact_set_title();

		contact_set_control_panel.update_row_in_contact_set = function (contact_set, contact_set_row, notes, status) {
			frappe.call({
				method: "simpatec.simpatec.report.contact_set_action_panel.contact_set_action_panel.update_row_in_contact_set",
				args: {
					contact_set: contact_set,
					contact_set_row: contact_set_row,
					notes: notes,
					status: status
				},
				callback: function (r) {
					if (r.message && r.message.status === "updated") {
						frappe.ui.hide_open_dialog();
						report.refresh();
					}
				}
			})
		}

		getLogsHtml = function (contact_set, contact_set_row) {
			let rowLogInfoHtmlOutput = "";
			let html_segment = ""
			frappe.call({
				method: "simpatec.simpatec.report.contact_set_action_panel.contact_set_action_panel.get_row_log",
				args: {
					contact_set,
					contact_set_row
				},
				async: false,
				callback:  function (r) {
					let row_log = r.message;
					row_log.forEach(log => {
						let date = log["date"];
						let event = log["event"];
						let notes = log["notes"];
						let owner = log["owner"];
						let status = log["status"];
						let status_color = log["status_color"];
						if (date) {
							let status_color_html = (status_color) ? `class="indicator-pill ${status_color}"`: ``;
							let status_html = (status) ? `<span ${status_color_html}>${status}</span>` : ``;	
							let notes_html = (notes) ? `<span><i>${notes}</i></span>` : ``;	
							let divElement = `<div><p>${date} ${status_html}</p><p>${owner}: ${notes_html}</p></div>`;
							rowLogInfoHtmlOutput += divElement;
						}
					});

					if (rowLogInfoHtmlOutput) {
						html_segment =  `<div class="form-group" >
							<div class="clearfix">
								<label class="control-label" style="padding-right: 0px;"></label>
								<span class="help"></span>
							</div>
							<div class="like-disabled-input" style="height: 230px; overflow: auto;">${rowLogInfoHtmlOutput}</div>
						</div>`
					}
				}
			})
			return html_segment;
		}

		getContactInfoHtml = function (contactInfo, field, linkType, label, contact_set, contact_set_row) {
			let contactInfoHtmlOutput = "";
			let html_segment = "";

			let linkPrefix = (linkType === "email") ? "mailto:" : "tel:";
			let action = (linkType === "email") ? "Sending Email to" : "Outgoing Call on";		
			contactInfo.forEach(infoObj => {
				let contact_medium = infoObj[field.toLowerCase()];
				let link = `${linkPrefix}${contact_medium}`;
				let notes = `${action} ${contact_medium}`
				let divElement = `<p><span><button type="button" class="btn btn-primary btn-sm"><a href="${link}" onclick="contact_set_control_panel.update_row_in_contact_set('${contact_set}', '${contact_set_row}', '${notes}')">📞</a></button></span><span>${contact_medium}</span></p>`;

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
			return html_segment;
		}

		contact_set_control_panel.open_dialog = function (row) {
			let contact_set = (row["contact_set"] === "null") ? null : row["contact_set"];
			let contact_set_row = (row["contact_set_row"] === "null") ? null : row["contact_set_row"];
			let status = (row["status"] === "null") ? null : row["status"];
			let emails = (row["emails"] === "null") ? null : row["emails"];
			let phone_nos = (row["phone_nos"] === "null") ? null : row["phone_nos"];
			let first_name = (row["first_name"] === "null") ? null : row["first_name"];
			let last_name = (row["last_name"] === "null") ? null : row["last_name"];
			let contact_name = (first_name && last_name) ? `${first_name} ${last_name}` : first_name;

			let dialog = new frappe.ui.Dialog({
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
						options: getContactInfoHtml(emails, "email_id", "email", "Emails", contact_set, contact_set_row),
						hidden: 1
					},
					{
						label: "Phone Nos",
						fieldname: "phone_nos",
						fieldtype: "HTML",
						options: getContactInfoHtml(phone_nos, "phone", "phone", "Phone Nos", contact_set, contact_set_row)
					},
					{
						fieldname: "colbreak1234",
						fieldtype: "Column Break"
					},
					{
						label: "Log Data",
						fieldname: "logs_data",
						fieldtype: "HTML",
						options: getLogsHtml(contact_set, contact_set_row)
					},
					{
						fieldname: "colbreak1235",
						fieldtype: "Column Break"
					},
					{
						label: "Status",
						fieldname: "status",
						fieldtype: "Select",
						options: "\nNew\nIn Work\nRejected\nOpportunity\nOpportunity Created",
						default: status
					},
					{
						label: "Notes",
						fieldname: "notes",
						fieldtype: "Small Text"
					},
				],
				primary_action_label: "Update",
				primary_action() {
					var data = dialog.get_values();
					contact_set_control_panel.update_row_in_contact_set(contact_set, contact_set_row, data.notes, data.status);
					// dialog.hide();
				}
			});
			dialog.show();
		}
	},
	get_datatable_options(options) {
		return Object.assign(options, {
			dynamicRowHeight: true,
			cellHeight: 40,
			layout: "fluid",
		});
	}
};

async function  add_contact_to_contact_set(report) {
	let contact_set = frappe.query_report.get_filter_value('contact_set');
	if (!contact_set) {
		frappe.throw("Please set Contact Set Filter");
	}

	const d =  new frappe.ui.Dialog({
		title: "Select Contacts",
		fields: [
			{
				fieldtype: "HTML",
				fieldname: "filter_area",
			},
			{
				fieldtype: "Table",
				fieldname: "contacts",
				cannot_add_rows: true,
				cannot_delete_rows: true,
				in_place_edit: true,
				// editable_grid: false,
				data: [],
				read_only: 1,
				fields: [
					{
						label: __("Contact"),
						fieldname: "contact",
						fieldtype: "Link",
						options: "Contact",
						in_list_view: true,
						read_only: 1,
						columns: 2
					},
					{
						label: __("Contact Row"),
						fieldname: "contact_row",
						fieldtype: "Data",
						options: "Contact",
						read_only: 1,
						hidden: 1
					},
					{
						label: __("First Name"),
						fieldname: "first_name",
						fieldtype: "Data",
						in_list_view: true,
						read_only: 1,
						columns: 3
					},
					{
						label: __("Last Name"),
						fieldname: "last_name",
						fieldtype: "Data",
						in_list_view: true,
						read_only: 1,
						columns: 3
					},
					{
						label: __("Email Address"),
						fieldname: "email_address",
						fieldtype: "Data",
						in_list_view: true,
						read_only: 1,
						columns: 2
					}
				]
			},
			{
				label: __("Show More"),
				fieldtype: "Button",
				fieldname: "show_more",
				click: async function() {
					let filters = filter_list.get_filters();
					limit = limit + cint(d.get_value('row_count'));
					await get_contacts(filters, limit, d);
				}
			},
			{
				fieldtype: "Int",
				fieldname: "row_count",
				read_only: 1,
				default: 0
			}
		],
		size: "extra-large",
		primary_action_label: __("Add rows in Contact Set"),
		primary_action: () => {
			let bulk_update_rows = d.fields_dict.contacts.grid.get_selected_children();
			if (bulk_update_rows.length < 1){
				frappe.throw("Please select Atleast 1 Contact Row");
			}
			
			frappe.call({
				method: "simpatec.simpatec.report.contact_register.contact_register.bulk_update_row_in_contact_set",
				// freeze: true,
				args: {
					contact_set: contact_set,
					bulk_update_rows: bulk_update_rows
				},
				callback: function (r) {
					frappe.query_report.refresh();
					frappe.msgprint(__(`Bulk Added Contacts to  <a href="/app/contact-set/${contact_set}" style="font-weight: bold;">${contact_set}</a> ✅`));
				}
			})
			d.hide();
		},
	});
	let limit = 100;

	let filter_list = new frappe.ui.FilterGroup({
		parent: d.get_field("filter_area").$wrapper,
		doctype: "Contact",
		default_filters: [],
		parent_doctype: "Contact",
		on_change: async() => {
			let filters = filter_list.get_filters();
			await get_contacts(filters, limit, d);
		}
	});
	// 'Apply Filter' breaks since the filers are not in a popover
	// Hence keeping it hidden
	filter_list.wrapper.find(".apply-filters").hide();
	await get_contacts([], limit, d);
	d.show();

}

async function get_contacts(filters, limit, dialog) {
	let dialog_contacts = [];
	await frappe.call({
		method: "simpatec.simpatec.report.contact_register.contact_register.execute",
		args: {
			filters: filters,
			limit: limit
		},
		freeze: true,
		freeze_message: "Loading data..."
	}).then(r => {
		// debugger;
		if (r.message[1] && r.message[1].length > 0) {
			r.message[1].forEach(contact => {
				dialog_contacts.push(
					{
						"contact": contact.contact,
						"contact_row": contact.contact_row,
						"first_name": contact.first_name,
						"last_name": contact.last_name,
						"email_address": contact.email_address
					});
			});
		} else {

		}
		dialog.fields_dict.contacts.grid.grid_pagination.page_length = limit;
		dialog.fields_dict.contacts.df.data = dialog_contacts;
		dialog.set_value("row_count", dialog_contacts.length);
		dialog.fields_dict.contacts.grid.refresh();
	})
}

function set_contact_set_title() {
	let contact_set_title_wrapper = $('.contact-set-title');
	let contact_set = frappe.query_report.get_filter_value('contact_set');
	if (contact_set) {
		frappe.db.get_value("Contact Set", contact_set, "title", function(value) {
			contact_set_title_wrapper.remove();
			contact_set_title_wrapper = `<div class="contact-set-title mt-2 col-md-6" data-fieldtype="HTML"><h3><i>${value["title"]}</i></h3></div>`;
			$('div[id="page-query-report"]').find('.page-form.flex').append(contact_set_title_wrapper);
		});
	} else {
		contact_set_title_wrapper.remove();
	}
}

function get_default_standard_action_html() {
	// copied from report source 
	return `<div class="standard-actions flex">      <span class="page-icon-group hidden-xs hidden-sm"><button class="text-muted btn btn-default  icon-btn" title="" data-original-title="Refresh">
	<svg class="icon  icon-sm" style="">
<use class="" href="#icon-refresh"></use>
</svg>
</button></span>      <div class="menu-btn-group">       <button type="button" class="btn btn-default icon-btn" data-toggle="dropdown" aria-expanded="false" title="" data-original-title="Menu">        <span>         <span class="menu-btn-group-label" data-label="">          <svg class="icon icon-sm">           <use href="#icon-dot-horizontal">           </use>          </svg>         </span>        </span>       </button>       <ul class="dropdown-menu dropdown-menu-right" role="menu" style=""><li class="user-action">
		<a class="grey-link dropdown-item visible-xs" href="#" onclick="return false;">
			
			<span class="menu-item-label" data-label="Refresh"><span class="alt-underline">R</span>efresh</span>
		</a>
	</li><li class="dropdown-divider user-action"></li><li>
		<a class="grey-link dropdown-item" href="#" onclick="return false;">
			
			<span class="menu-item-label" data-label="Edit"><span class="alt-underline">E</span>dit</span>
		</a>
	</li><li>
		<a class="grey-link dropdown-item" href="#" onclick="return false;">
			
			<span class="menu-item-label" data-label="Print"><span class="alt-underline">P</span>rint</span>
		</a>
	</li><li>
		<a class="grey-link dropdown-item" href="#" onclick="return false;">
			
			<span class="menu-item-label" data-label="PDF">P<span class="alt-underline">D</span>F</span>
		</a>
	</li><li>
		<a class="grey-link dropdown-item" href="#" onclick="return false;">
			
			<span class="menu-item-label" data-label="Export">E<span class="alt-underline">x</span>port</span>
		</a>
	</li><li>
		<a class="grey-link dropdown-item" href="#" onclick="return false;">
			
			<span class="menu-item-label" data-label="Setup%20Auto%20Email">Se<span class="alt-underline">t</span>up Auto Email</span>
		</a>
	</li><li>
		<a class="grey-link dropdown-item" href="#" onclick="return false;">
			
			<span class="menu-item-label" data-label="Add%20Column"><span class="alt-underline">A</span>dd Column</span>
		</a>
	</li><li>
		<a class="grey-link dropdown-item" href="#" onclick="return false;">
			
			<span class="menu-item-label" data-label="User%20Permissions"><span class="alt-underline">U</span>ser Permissions</span>
		</a>
	</li><li>
		<a class="grey-link dropdown-item" href="#" onclick="return false;">
			
			<span class="menu-item-label" data-label="Save">Sa<span class="alt-underline">v</span>e</span>
		</a>
	</li></ul>      </div>      <button class="btn btn-secondary btn-default btn-sm hide"></button>      <div class="actions-btn-group hide">       <button type="button" class="btn btn-primary btn-sm" data-toggle="dropdown" aria-expanded="false">        <span>         <span class="hidden-xs actions-btn-group-label" data-label="Actions"><span class="alt-underline">A</span>ctions</span>         <svg class="icon icon-xs">          <use href="#icon-select">          </use>         </svg>        </span>       </button>       <ul class="dropdown-menu dropdown-menu-right" role="menu">       </ul>      </div>      <button class="btn btn-primary btn-sm hide primary-action"></button>     </div>`
}