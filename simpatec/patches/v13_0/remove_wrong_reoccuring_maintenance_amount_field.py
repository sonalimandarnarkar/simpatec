import frappe

def execute():
    if frappe.db.exists("Custom Field", "Sales Order Item-reoccuring_maintenance_amount"):
        frappe.delete_doc("Custom Field", "Sales Order Item-reoccuring_maintenance_amount", force=1)