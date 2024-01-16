frappe.ui.form.on('Software Maintenance', {
    refresh(frm) {
        frm.add_custom_button('Software Maintenance', function () { 
            debugger;

            frappe.call({
                method: "simpatec.events.sales_order.make_sales_order",
                args: {
                    software_maintenance: frm.doc.name,
                    debug: 1
                },
                callback: function (r) {
                    frm.set_value("total_subscribers", r.message);
                },
            });

            // frappe.prompt(
            //     {
            //         fieldtype: "Date",
            //         label: __("Trigger Date"),
            //         fieldname: "trigger_date",
            //         reqd: 1,
            //     },
            //     function (data) {
            //         frappe.call({
            //             method: "simpatec.events.sales_order.make_sales_order",
            //             args: {
            //                 software_maintenance: frm.doc.name,
            //                 // trigger_date: data.trigger_date,
            //             },
            //             callback: function (r) {
            //                 frm.set_value("total_subscribers", r.message);
            //             },
            //         });
            //     },
            //     __("Import Subscribers"),
            //     __("Import")
            // );
            
        }, __("Create Sales Order"));
    }
})