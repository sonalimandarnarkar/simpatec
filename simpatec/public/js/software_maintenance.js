frappe.ui.form.on('Software Maintenance', {
    refresh(frm) {
        frm.add_custom_button('Software Maintenance', function () { 
            frappe.call({
                method: "simpatec.events.sales_order.make_sales_order",
                args: {
                    software_maintenance: frm.doc.name,
                    background_job: false
                },
                callback: function (r) {
                    frm.set_value("total_subscribers", r.message);
                },
            });
        }, __("Create Sales Order"));
    }
})