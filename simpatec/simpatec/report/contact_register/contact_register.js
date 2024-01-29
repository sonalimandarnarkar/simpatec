// Copyright (c) 2024, Phamos GmbH and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.provide("contact_register")
frappe.query_reports["Contact Register"] = {
	"filters": [],

	"bulk_update_rows": [],

	onload: async function (report) {
		$(".custom-actions").hide();
		$(".standard-actions").hide();
		make_filter_list();
		$(".page-actions").append(`<button class="btn btn-default btn-sm ellipsis contact-set-route" onclick="bulk_update_contact_set()">Add selected to Contact Set</button>`);
		$(".page-actions").append(`<button class="btn btn-default btn-sm ellipsis contact-set-route" onclick="route_to_contact_set()">Go to Contact Set</button>`);

		contact_register.open_dialog = function (contact, contact_row) {
			let d = new frappe.ui.Dialog({
				title: "Enter details",
				fields: [
					{
						label: "Contact Set",
						fieldname: "contact_set",
						fieldtype: "Link",
						options: "Contact Set",
						reqd: 1
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
						}
					})

					d.hide();
				}
			});
			d.show();
		}
	}
};

function route_to_contact_set() {
	frappe.set_route("List", "Contact Set");
	$(".contact-set-route").hide();
}

function update_bulk_list(contact, contact_row) {
	let id_contact_row = "#" +  contact_row;
	$(id_contact_row).on("change",function(){
		var _val = $(this).is(":checked") ? "checked" : "unchecked";
		console.log(_val);
		if (_val == "checked") {
			// if checked then add object {contact, contact_row} if not existt in array frappe.query_reports["Contact Register"]["bulk_update_rows"]
            let exists = frappe.query_reports["Contact Register"]["bulk_update_rows"].some(item => item.contact === contact && item.contact_row === contact_row);
            if (!exists) {
                frappe.query_reports["Contact Register"]["bulk_update_rows"].push({ contact, contact_row });
            }
		} else {
			// if unchecked then search and remove object {contact, contact_row} from array frappe.query_reports["Contact Register"]["bulk_update_rows"]
			frappe.query_reports["Contact Register"]["bulk_update_rows"] = frappe.query_reports["Contact Register"]["bulk_update_rows"].filter(item => !(item.contact === contact && item.contact_row === contact_row));
		}
	});
}

function bulk_select_all() {
	$(".bulk-select-all").on("change",function(){
		let _val = $(this).is(":checked") ? "checked" : "unchecked";
		frappe.query_reports["Contact Register"]["bulk_update_rows"] = [];
		if (_val == "checked") {
			$(".bulk-select-contact-set").prop('checked', true);
			$(".bulk-select-contact-set:checked").each(function() {
				let contact = $(this).data("contact");
				let contact_row = $(this).data("contact-row");
				frappe.query_reports["Contact Register"]["bulk_update_rows"].push({ contact, contact_row })
			  });
		} else {
			$(".bulk-select-contact-set").prop('checked', false);
			frappe.query_reports["Contact Register"]["bulk_update_rows"] = [];
		}
	});
}

function bulk_update_contact_set() {
	let bulk_update_rows = frappe.query_reports["Contact Register"]["bulk_update_rows"];
	if (bulk_update_rows.length === 0) {
		frappe.msgprint(__("Select atleast 1 row for Bulk Update"));
		return;
	}
	let d = new frappe.ui.Dialog({
		title: "Select Contact Set",
		fields: [
			{
				label: "Contact Set",
				fieldname: "contact_set",
				fieldtype: "Link",
				options: "Contact Set",
				reqd: 1
			}
		],
		primary_action_label: "Bulk Update",
		primary_action() {
			var data = d.get_values();
			frappe.call({
				method: "simpatec.simpatec.report.contact_register.contact_register.bulk_update_row_in_contact_set",
				freeze: true,
				args: {
					contact_set: data.contact_set,
					bulk_update_rows: bulk_update_rows
				},
				callback: function (r) {
					$(".bulk-select-all").prop('checked', false);
					$(".bulk-select-contact-set").prop('checked', false);
					frappe.query_reports["Contact Register"]["bulk_update_rows"] = [];
					frappe.msgprint(__(`Bulk Added Contacts to  <a href="/app/contact-set/${data.contact_set}" style="font-weight: bold;">${data.contact_set}</a> ✅`));
				}
			})
			d.hide();
		}
	});
	d.show();
}

var make_filter_list = function () {
	var filter_list_wrapper = $(".page-actions")
	$(`<div class="filter-selector">
		<button class="btn btn-default btn-sm filter-button">
			<span class="filter-icon">
				${frappe.utils.icon("filter")}
			</span>
			<span class="button-label hidden-xs">
				${__("Filter")}
			<span>
		</button>
	</div>`
	).appendTo(filter_list_wrapper);

	var filter_button = filter_list_wrapper.find(".filter-button");
	this.filter_list = new frappe.ui.FilterGroup({
		parent: filter_list_wrapper,
		doctype: "Contact",
		filter_button: filter_button,
		default_filters: [],
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
