# Copyright (c) 2024, Phamos GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import timedelta
from frappe.utils import now

class SimpaTecSettings(Document):
	pass


@frappe.whitelist()
def update_software_maintenance_items(update_timestamp=None):
    try:

        # Remove Wrong field of reccuring_maintenance_amount and reoccuring_maintenance_amount if exist
        if frappe.db.exists("Custom Field", "Sales Order Item-reoccuring_maintenance_amount"):
            frappe.delete_doc("Custom Field", "Sales Order Item-reoccuring_maintenance_amount", force=1)
        if frappe.db.exists("Custom Field", "Sales Order Item-reccuring_maintenance_amount"):
            # First set the value of wrong `reoccurring_maintenance_amount` field into `reoccurring_maintenance_amount`
            frappe.db.sql("update `tabSales Order Item` set `reoccurring_maintenance_amount` = `reccuring_maintenance_amount` where item_type = 'Maintenance Item'")
            # Now removing the field
            frappe.delete_doc("Custom Field", "Sales Order Item-reccuring_maintenance_amount", force=1)
        
        update_timestamp = int(update_timestamp)
        """Query for removing all previous Software maintenance Items"""
        frappe.db.sql("DELETE FROM `tabSoftware Maintenance Item`")
        software_maintenances = frappe.get_all("Software Maintenance", fields=["sales_order", "name"], filters=[["sales_order","is","set"]])
        for s_m in software_maintenances:
            so_items = frappe.get_all("Sales Order Item", filters={"parent": s_m.sales_order}, fields=["*"])
            if len(so_items) > 0:
                for item in so_items:   
                    software_maintenance_items = frappe.new_doc("Software Maintenance Item")

                    if item.start_date is not None:
                        item.start_date = item.start_date + timedelta(days=365)
                    if item.end_date is not None:
                        item.end_date = item.end_date + timedelta(days=365)
                        if item.start_date is not None and item.end_date is not None:
                            days_diff = item.end_date - item.start_date
                            if days_diff == 365:
                                item.end_date = item.end_date - timedelta(days=1)
                    if item.item_type == "Maintenance Item":
                        item.rate = item.reoccurring_maintenance_amount
                        item.reoccurring_maintenance_amount = item.reoccurring_maintenance_amount
                    else:
                        item.rate = 0
                        item.reoccurring_maintenance_amount = 0

                    software_maintenance_items.update({
                        "idx": item.idx,
                        "item_code": item.item_code,
                        "item_name": item.item_name,
                        "description": item.description,
                        "conversion_factor": item.conversion_factor,
                        "qty": item.qty,
                        "rate": item.reoccurring_maintenance_amount,
                        "reoccurring_maintenance_amount": item.reoccurring_maintenance_amount,
                        "uom": item.uom,
                        "item_language": item.item_language,
                        "delivery_date": frappe.db.get_value("Sales Order", s_m.sales_order, "transaction_date"),
                        "start_date": item.start_date,
                        "end_date": item.end_date,
                        # "einkaufspreis": item.einkaufspreis,
                        'parent': s_m.name,
                        'parentfield': 'items',
                        'parenttype': "Software Maintenance"
                    })
                    software_maintenance_items.insert(ignore_permissions=True)
                modified_by = frappe.session.user
                # frappe.db.set_value("Software Maintenance", s_m.name, "assign_to", frappe.db.get_value("Sales Order", s_m.sales_order, "assigned_to"), update_modified=False)
                frappe.db.set_value("Sales Order", s_m.sales_order, "sales_order_type", "First Sale", update_modified=update_timestamp)
                frappe.db.set_value("Sales Order", s_m.sales_order, "software_maintenance", s_m.name, update_modified=update_timestamp)
                if update_timestamp:
                    frappe.db.sql("""update `tabSoftware Maintenance` set `modified` = '{modified}', `modified_by` = '{modified_by}' where `name` = '{sm_name}'""".format(modified= now(), modified_by= modified_by, sm_name=s_m.name))
                    frappe.db.sql("""update `tabSales Order` set `sales_order_type` = 'Reoccuring Maintenance', `modified` = '{modified}', `modified_by` = '{modified_by}' where `sales_order_type` = 'Follow Up Maintenance' """.format(modified= now(), modified_by= modified_by))
                else:
                    frappe.db.sql("""update `tabSales Order` set `sales_order_type` = 'Reoccuring Maintenance' where `sales_order_type` = 'Follow Up Maintenance' """)
                frappe.db.commit()
        return {"message":"""<h3>The script has run and had updated all Software Maintenance:</h3>
                <ul>
                    <li>existing items table have been cleared from all Software Maintenance</li>
                    <li>the linked Sales Invoice in Software Maintenance has been updated to "First Sale"</li>
                    <li>the items from that Sales Invoice have been fetched into the Software Maintenance item table</li>
                    <li>all Sales Orders with sales_order_type "Follow-Up Maintenance have been updated to "Reoccurring Maintenance"</li>
                </ul>
                <p>The script has ignored missing date like start/end dates, rates, etc.</p>
                <p>For further information check in SimpaTec Settings page and consult your project manager.</p> """, "title": "Success"}   
    except Exception as ex:
        frappe.db.rollback()
        frappe.log_error(ex)
        return {"message":"There was some error occured in the process, Please check error logs.", "title":"Error" }