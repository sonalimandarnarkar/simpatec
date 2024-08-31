// Copyright (c) 2024, Phamos GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on('SimpaTec Settings', {
	update_software_maintenance_items: function(frm){
		frm.call({
			method: "update_software_maintenance_items",
			doc: frm.doc,
			args: {
				update_timestamp: frm.doc.update_timestamp
			},
			callback: function (r) {
				if (r.message) {
					frappe.msgprint(r.message)
				}
			}
		})
	},
	update_item_fields: function(frm){
		frm.call({
			method: "update_item_details",
			doc: frm.doc,
			args: {
				update_timestamp: frm.doc.update_timestamp
			},
			freeze: 1,
			freeze_message: __("Updating System"),
			callback: function (r) {
				if (r.message) {
					frappe.msgprint(r.message)
				}
			}
		})
	}
});
