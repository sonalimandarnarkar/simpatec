// Copyright (c) 2023, Phamos GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on('Software Maintenance', {
    refresh(frm) {
        var reoccurring_label = __(`${frm.doc.licence_renewal_via} (Reoccurring Maintenance)`)
        frm.add_custom_button(reoccurring_label, function () {
            if(frm.doc.licence_renewal_via == "Quotation"){
                var d = new frappe.ui.Dialog({
                    title: __('Quotation Mandatory Fields'),
                    fields: [
                        {
                            "label": "Item Group",
                            "fieldname": "item_group",
                            "fieldtype": "Link",
                            "options": "Item Group",
                            "default": frm.doc.item_group,
                            "reqd": 1,
                        },
                        {
                            "label": "Quotation Label",
                            "fieldname": "quotation_label",
                            "fieldtype": "Link",
                            "options": "Angebotsvorlage",
                            "reqd": 1,
                        },
                        {
                            "label": "Ihr Ansprechpartner",
                            "fieldname": "ihr_ansprechpartner",
                            "fieldtype": "Link",
                            "options": "Employee",
                            "reqd": 1,
                        },

                    ],
                    primary_action: function (data) {
                        frm.events.make_reoccurring(frm, data)
                        d.hide();
                    },
                    primary_action_label: __('Create Quotation')
                });
                d.show();
            }else{
                frm.events.make_reoccurring(frm)
            }
        }, __("Create"));


        //hide all + in the connection
        $('.form-documents button').hide();
    },
    make_reoccurring(frm, mandatory_fields){
        frappe.call({
            method: "simpatec.simpatec.doctype.software_maintenance.software_maintenance.make_reoccuring_sales_order",
            args: {
                software_maintenance: frm.doc.name,
                is_background_job: 0,
                licence_renewal_via: frm.doc.licence_renewal_via,
                mandatory_fields: mandatory_fields
            },
            callback: function (r) {
            },
        });
    },

    set_inflation(frm){
        var inflation_item = frappe.call({
            method: 'frappe.client.get_value',
            args: {
                'doctype': 'Item',
                'filters': { 'item_type': "Inflation Item" },
                'fieldname': [
                    'name',
                    'item_name',
                    'stock_uom',
                    'item_type'                
                ]
            },
            async: false,
            callback: function (r) {
                if (!r.exc) { 
                    $.each(frm.doc.items, function (k, v) {
                        if (v.item_type == "Maintenance Item") {
                            // Inflation Rate calculation
                            var inflation_rate = 0
                            var inflation_amount = 0
                            var increased_reoccurring_amount = 0
                            
                            if(v.start_date > frm.doc.inflation_valid_from){
                                var inflation_rate = frm.doc.inflation_rate
                                var inflation_amount = (v.reoccurring_maintenance_amount * inflation_rate) / 100
                                var increased_reoccurring_amount = v.reoccurring_maintenance_amount + inflation_amount
                            }

                            // Add inflation Item next to Maintenance Item
                            let item_row = cur_frm.add_child("items");
                            frappe.model.set_value(item_row.doctype, item_row.name, "item_code", r.message.name);
                            frappe.model.set_value(item_row.doctype, item_row.name, "item_name", r.message.item_name);
                            frappe.model.set_value(item_row.doctype, item_row.name, "uom", r.message.stock_uom);
                            frappe.model.set_value(item_row.doctype, item_row.name, "item_type", r.message.item_type);
                            frappe.model.set_value(item_row.doctype, item_row.name, "rate", inflation_amount);
                            frappe.model.set_value(item_row.doctype, item_row.name, "price_list_rate", inflation_amount);
                            frappe.model.set_value(item_row.doctype, item_row.name, "description", `Adding ${frm.doc.inflation_rate}% Inflation Rate from the ${frm.doc.inflation_valid_from}`);
                            
                            // New Increase Reoccurring Amount 
                            frappe.model.set_value(v.doctype, v.name, "reoccurring_maintenance_amount", increased_reoccurring_amount)
                            
                            frm.doc.items.splice(k+1, 0, item_row);
                            frm.doc.items.pop()
                        }
                    })
                    frm.refresh_field("items");
                    frm.fields_dict["items"].grid.renumber_based_on_dom()
                    frm.refresh_field("items");  
                }
            }
        });
        
    }
});

frappe.ui.form.on('Software Maintenance Item', {
    item_code(frm, cdt, cdn){
        // set_right_translation(frm, cdt, cdn)

        var item = frappe.get_doc(cdt, cdn);
        item.pricing_rules = ''
        if (item.item_code && item.uom) {
            return frm.call({
                method: "erpnext.stock.get_item_details.get_conversion_factor",
                args: {
                    item_code: item.item_code,
                    uom: item.uom
                },
                callback: function (r) {
                    if (!r.exc) {
                        frappe.model.set_value(cdt, cdn, 'conversion_factor', r.message.conversion_factor);
                    }
                }
            });
        }
    },
});

var set_right_translation = function(frm, cdt, cdn){
    var item_language = frappe.model.get_value(cdt, cdn, "item_language")
    var grid = frm.fields_dict['items'].grid;
    if (item_language === "en"){
        grid.update_docfield_property("item_name_en", "hidden", 0)
        grid.update_docfield_property("description_en", "hidden", 0)
        grid.update_docfield_property("item_name_de", "hidden", 1)
        grid.update_docfield_property("description_de", "hidden", 1)
        grid.update_docfield_property("item_name_fr", "hidden", 1)
        grid.update_docfield_property("description_fr", "hidden", 1)
    } else if (item_language === "de"){
        grid.update_docfield_property("item_name_en", "hidden", 1)
        grid.update_docfield_property("description_en", "hidden", 1)
        grid.update_docfield_property("item_name_de", "hidden", 0)
        grid.update_docfield_property("description_de", "hidden", 0)
        grid.update_docfield_property("item_name_fr", "hidden", 1)
        grid.update_docfield_property("description_fr", "hidden", 1)
    } else if (item_language === "fr"){
        grid.update_docfield_property("item_name_en", "hidden", 1)
        grid.update_docfield_property("description_en", "hidden", 1)
        grid.update_docfield_property("item_name_de", "hidden", 1)
        grid.update_docfield_property("description_de", "hidden", 1)
        grid.update_docfield_property("item_name_fr", "hidden", 0)
        grid.update_docfield_property("description_fr", "hidden", 0)
    }
    grid.refresh();

    var item_code = frappe.model.get_value(cdt, cdn, "item_code")
    frappe.db.get_value("Item", item_code, ["in_en", "id_en", "in_de", "id_de", "in_fr", "id_fr"]).then((r) => {
        frappe.model.set_value(cdt, cdn, "item_name_en", r.message.in_en)
        frappe.model.set_value(cdt, cdn, "description_en", r.message.id_en)
        frappe.model.set_value(cdt, cdn, "item_name_de", r.message.in_de)
        frappe.model.set_value(cdt, cdn, "description_de", r.message.id_de)
        frappe.model.set_value(cdt, cdn, "item_name_fr", r.message.in_fr)
        frappe.model.set_value(cdt, cdn, "description_fr", r.message.id_fr)
    })
}