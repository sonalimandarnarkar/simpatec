import frappe
from datetime import timedelta
from frappe.utils import now

@frappe.whitelist()
def execute():
    try:
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
                    # if item.item_type == "Maintenance Item":
                    #     item.rate = item.reoccuring_maintenance_amount
                    #     item.reoccuring_maintenance_amount = item.reoccuring_maintenance_amount
                    # else:
                    #     item.rate = 0
                    #     item.reoccuring_maintenance_amount = 0

                    software_maintenance_items.update({
                        "idx": item.idx,
                        "item_code": item.item_code,
                        "item_name": item.item_name,
                        "description": item.description,
                        "conversion_factor": item.conversion_factor,
                        "qty": item.qty,
                        "rate": item.reoccuring_maintenance_amount,
                        "reoccuring_maintenance_amount": item.reoccuring_maintenance_amount,
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
                frappe.db.sql("""update `tabSoftware Maintenance` set `modified` = '{modified}', `modified_by` = '{modified_by}' where `name` = '{sm_name}'""".format(modified= now(), modified_by= modified_by, sm_name=s_m.name))
                frappe.db.set_value("Sales Order", s_m.sales_order, "sales_order_type", "First Sale")
                frappe.db.sql("""update `tabSales Order` set `sales_order_type` = 'Reoccuring Maintenance', `modified` = '{modified}', `modified_by` = '{modified_by}' where `sales_order_type` = 'Follow Up Maintenance' """.format(modified= now(), modified_by= modified_by))
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