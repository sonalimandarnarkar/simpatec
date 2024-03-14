frappe.ui.form.on('Sales Order', {
    onload(frm){
        // FILTER SALES ORDER WITH RESPECTIVE CONDITIONS
        frm.set_query('sales_order', 'sales_order_clearances', function () {
            return {
                filters: {
                    "name": ["!=", frm.doc.name],
                    "sales_order_type": ["!=", "Internal Clearance"],
                    "eligable_for_clearance": 1,
                    "docstatus": 1
                },
            };
        });
    },

    refresh(frm) {
        // GET SIMPATEC GLOBAL SETTINGS
        frm.events.get_simpatec_settings(frm)

        $('[data-doctype="Software Maintenance"]').find("button").hide();
        if (['First Sale', 'RTO', 'Subscription Annual'].includes(frm.doc.sales_order_type) && frm.doc.docstatus == 1 && !frm.doc.software_maintenance) {
            frm.add_custom_button('Software Maintenance', function () { 
                frappe.model.open_mapped_doc({
                    method: "simpatec.events.sales_order.make_software_maintenance",
        			frm: frm
        		})                
            }, __("Create"));
        }
    },

    get_simpatec_settings(frm){ // SIMPATECH GLOBAL SETTING FUNCTION
        frm.doc.clearance_item = ""
        frm.call({
            method: "frappe.client.get",
            args: {
                fieldname: "clearance_item",
                doctype: "SimpaTec Settings"
            },
            async: false,
            callback: function (r) {
                if (r.message) {
                    frm.doc.clearance_item = r.message.clearance_item; // SET CLEARANCE ITEM IN GLOBAL FRM VARIABLE.
                }
            }
        });
    }
})

// SALES ORDER CLEARANCE TABLE EVENTS
frappe.ui.form.on("Sales Order Clearances", {
    sales_order_clearances_add(frm, cdt, cdn){ // EVENT TRIGGER ON ADD ROW
        var cur_row = locals[cdt][cdn];
        if(!is_null(frm.doc.customer)){ // CHECK IF CUSTOMER IS EMPTY

            // CHECK THE SAME ROW INDEX OF ITEM TABLE, IF ROW IS NOT AVAILABLE 
            // THEN ADD NEW ROW IN ITEM TABLE, OTHERWISE UPDATE THE EXISTING INDEX ROW
            var item_row = frm.doc.items[cur_row.idx - 1];  // GET THE ITEM TABLE SAME ROW INDEX
            if (!is_null(item_row)) {
                // UPDATING SAME ROW INDEX IN ITEM TABLE
                frappe.model.set_value(item_row.doctype, item_row.name, "item_code", frm.doc.clearance_item)
            }else{
                // CREATE NEW ROW IN ITEM TABLE
                var row = frappe.model.add_child(frm.doc, "Sales Order Item", "items");
                frappe.model.set_value(row.doctype, row.name, "item_code", frm.doc.clearance_item)
            } 
            refresh_field("items");
            
        }
        else{
            // IF CUSTOMER NOT AVAILABLE THEN THROW WARNING MESSAGE
            frm.doc.sales_order_clearances = [];
            refresh_field("sales_order_clearances");
            frappe.msgprint("Please specify: Customer. It is needed to fetch Sales Order Details.")
        }
    },
    sales_order(frm, cdt, cdn){ // EVENT TRIGGER ON SALES ORDER FIELD
        var cur_row = locals[cdt][cdn];
        var item_row = frm.doc.items[cur_row.idx - 1];
        // CHECK IF ITEM ROW IS ALREADY AVAILABLE
        if (!is_null(item_row)){
            frappe.model.set_value(item_row.doctype, item_row.name, "start_date", cur_row.date)
            frappe.model.set_value(item_row.doctype, item_row.name, "description", `Clearance from ${cur_row.sales_order} ${cur_row.clearance_details}`)
        }
        refresh_field("items");
    },

})