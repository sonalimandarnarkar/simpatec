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
    }
})