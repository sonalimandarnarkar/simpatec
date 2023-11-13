import frappe


@frappe.whitelist()
def software_maintenance(item_group, customer):
    return frappe.get_all('Software Maintenance', filters={'item_group': item_group, 'customer': customer}, fields=["name", "status"])