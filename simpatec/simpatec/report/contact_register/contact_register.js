// Copyright (c) 2024, Phamos GmbH and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.provide("contact_register")
frappe.query_reports["Contact Register"] = {
	"filters": [],

	"bulk_update_rows": [],

	onload: async function (report) {
		if ($('body[data-route="query-report/Contact Register"]').length > 0) {
			let report_wrapper = $('body[data-route="query-report/Contact Register"]');
			let page_action_wrapper = report_wrapper.find('div[id="page-query-report"]').find(".page-head-content").find(".page-actions");
			page_action_wrapper.html(`
				<button class="btn btn-default btn-sm ellipsis contact-set-route ml-2 mr-2" onclick="bulk_update_contact_set()">Add selected to Contact Set</button>
				<button class="btn btn-default btn-sm ellipsis contact-set-route" onclick="route_to_contact_set()">Switch to Contact Set</button>
				<div class="control-input flex align-center" id="load-more-contacts"></div>
				<div class="filter-selector">
					<button class="btn btn-default btn-sm filter-button">
						<span class="filter-icon">
							${frappe.utils.icon("filter")}
						</span>
						<span class="button-label hidden-xs">
							${__("Filter")}
						<span>
					</button>
				</div>
			`);
			
			setup_paging_area(page_action_wrapper);
			make_filter_list(page_action_wrapper);
			// bulk_set_render_in_checkbox_col(page_action_wrapper);
		}

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
	},
	after_datatable_render: function(datatable_obj) {
		$(datatable_obj.wrapper).find("div[title='Bulk Select']").html('<input class="bulk-select-all" type="checkbox" onclick="bulk_select_all()" />');
	},
	get_datatable_options(options) {
		return Object.assign(options, {
			dynamicRowHeight: true,
			cellHeight: 45,
		});
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


function setup_paging_area(page_action_wrapper) {

	const paging_values = [100, 500];

	this.$paging_area = `<div class="list-paging-area level">
							<div class="level-left">
								<div class="btn-group">
									${paging_values
										.map(
											(value) => `
										<button type="button" class="btn btn-default btn-sm btn-paging"
											data-value="${value}">
											${value}
										</button>
									`
										)
										.join("")}
								</div>
							</div>
							<div class="level-right">
								<button class="btn btn-default btn-more btn-sm">
									${__("Load More")}
								</button>
							</div>
						</div>`;
	page_action_wrapper.find('div[id="load-more-contacts"]').html(this.$paging_area);

	// set default paging btn active
	page_action_wrapper.find(`.btn-paging[data-value="100"]`).addClass("btn-info");
	// this.$paging_area.find(`.btn-paging[data-value="${this.page_length}"]`).addClass("btn-info");
	page_action_wrapper.on("click", ".btn-paging, .btn-more", (e) => {
		const $this = $(e.currentTarget);

		if ($this.is(".btn-paging")) {
			// set active button
			page_action_wrapper.find(".btn-paging").removeClass("btn-info");
			$this.addClass("btn-info");

			this.start = $this.data().value;
			this.page_length = this.selected_page_count = $this.data().value;
		} else if ($this.is(".btn-more")) {
			this.start = this.start + this.page_length;
			this.page_length = this.selected_page_count || 20;
		}
		let filters = this.filter_list.get_filters();
		let limit = this.start;

		get_and_render_data(filters, limit);
		// this.refresh();
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
					frappe.msgprint(__(`Contact has been added to  <a href="/app/contact-set/${data.contact_set}" style="font-weight: bold;">${data.contact_set}</a> ✅. 
					Would you like to: <ol>
							<li><a href="#">Go back to Contact Register and add further Contacts</a></li>
							<li><a href="/app/query-report/Contact Set Action Panel">Switch to the Contact Set Action Panel</a></li>
						</ol>`
				  	));
				}
			})
			d.hide();
		}
	});
	d.show();
}

var make_filter_list = function (page_action_wrapper) {
	var filter_button = page_action_wrapper.find(".filter-button");
	this.filter_list = new frappe.ui.FilterGroup({
		parent: page_action_wrapper,
		doctype: "Contact",
		filter_button: filter_button,
		default_filters: [],
		on_change: () => {
			var filters = this.filter_list.get_filters();
			let limit = 100;
			get_and_render_data(filters, limit);
		},
	});
}

var get_and_render_data = function(filters, limit){
	frappe.call({
		method: "simpatec.simpatec.report.contact_register.contact_register.execute",
		args: {
			filters: filters,
			limit: limit
		},
		freeze: true,
		freeze_message: "Loading data..."
	}).then(r => {
		if (r.message){
			$(".report-wrapper").next().hide()
		}
		var data = {
			columns: r.message[0],
			result: r.message[1],
			total_count: r.message[2]
		}
		frappe.query_report.prepare_report_data(data);
		frappe.query_report.render_datatable();
		frappe.query_report.show_status(data["total_count"]);
	})
}
