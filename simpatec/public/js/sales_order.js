frappe.ui.form.on('Sales Order', {
    refresh(frm) {
        $('[data-doctype="Software Maintenance"]').find("button").hide();
        if (!frm.doc.software_maintenance && frm.doc.docstatus == 0) {
            frm.add_custom_button('Software Maintenance', function () { 
                frappe.model.open_mapped_doc({
                    method: "simpatec.events.sales_order.make_software_maintenance",
        			frm: frm
        		})                
            }, __("Create"));
        }
    }
})