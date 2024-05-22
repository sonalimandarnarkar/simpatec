// Copyright (c) 2024, Phamos GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on('SimpaTec Settings', {
	refresh: function(frm) {
		frm.add_custom_button("Update Software Maintenance Items", function(){
			frm.call({
				method: "simpatec.patches.v13_0.fixture_set_sales_order_items.execute",
				callback: function (r) {
					if(r.message){
						frappe.msgprint(r.message)
					}
				}
			})
		})
	}
});
