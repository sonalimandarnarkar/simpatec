frappe.ui.form.on('Sales Order', {
    refresh(frm) {
        if (frm.doc.sales_order_type == 'First Sale' && frm.doc.docstatus == 1) {
            frm.add_custom_button('Software Maintenance', function () { 
                frappe.model.open_mapped_doc({
                    method: "simpatec.events.sales_order.make_software_maintenance",
        			frm: frm
        		})                
            }, __("Create"));
        }

        frm.events.toggle_software_maintenance_reqd(frm);
    },

    sales_order_type(frm) {
        frm.events.toggle_software_maintenance_reqd(frm);
    },

    toggle_software_maintenance_reqd(frm) {
        if (frm.doc.sales_order_type == 'Follow Up Maintenance') {
            frm.set_df_property('software_maintenance', 'reqd', true);
        } else {
            frm.set_df_property('software_maintenance', 'reqd', false);
        }
    }
})