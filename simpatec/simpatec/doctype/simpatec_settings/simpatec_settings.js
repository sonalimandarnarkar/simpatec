// Copyright (c) 2024, Phamos GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on('SimpaTec Settings', {
	update_software_maintenance_items: function(frm){
		frm.call({
			method: "simpatec.simpatec.doctype.simpatec_settings.simpatec_settings.update_software_maintenance_items",
			args: {
				update_timestamp: frm.doc.update_timestamp
			},
			callback: function (r) {
				if (r.message) {
					frappe.msgprint(r.message)
				}
			}
		})
	}
});
