// Copyright (c) 2023, Phamos GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on('Software Maintenance', {
    refresh(frm) {
        frm.add_custom_button('Software Maintenance', function () { 
            frappe.call({
                method: "simpatec.events.sales_order.make_sales_order",
                args: {
                    software_maintenance: frm.doc.name,
                    is_background_job: 0
                },
                callback: function (r) {
                },
            });
        }, __("Renew Sales Order"));
    }
});
