import frappe

def execute():
	contact_set_rows = frappe.get_all("Contact Set Contacts", fields=["contact", "contact_row", "name", "link_name", "link_doctype", "link_title"], filters=[["contact","is","set"], ["contact_row","is","set"], ["link_name","is","set"], ["link_doctype","is","set"], ["link_title","=",""] ])
	for contact in contact_set_rows:
		link_title = frappe.db.get_value("Dynamic Link", {"name": contact.contact_row, "link_name": contact.link_name, "link_doctype": contact.link_doctype}, ["link_title"])
		if link_title:
			frappe.db.set_value("Contact Set Contacts", contact.name, "link_title", link_title)
