import frappe


@frappe.whitelist()
def software_maintenance(customer):
    return frappe.get_all('Software Maintenance', filters={'customer': customer}, fields=["name", "status", "performance_period_end"])