# Copyright (c) 2024, Phamos GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	data = get_data(filters)
	columns = get_columns()
	return columns, data



def get_data(filters):
	data = frappe.db.sql(
		"""
		select c.name as contact, dl.name as contact_row, c.first_name, c.last_name, c.email_id, 
		dl.link_doctype as ref_type, dl.link_name as ref_name
		from
			`tabContact` c, `tabDynamic Link` dl
		where dl.parent = c.name and dl.link_doctype in ('Customer', 'Supplier')""",
		as_dict=1,
	)

	for d in data:
		d['contact_reference'] = '<a href="/app/Form/{0}/{1}" >Customer {1}</a>'.format(d.get('ref_type'), d.get('ref_name'))
		d['add_to_contact_group'] ='<button class="btn btn-sm" onclick="contact_register.open_dialog({0}, {1})">{2}</button>'.format("'" + d.contact + "'", "'" + d.contact_row + "'",  _("Add to Contact Set"))
	
	return data


def get_columns():
	columns = [
		{
			"label": _("Action"),
			"fieldtype": "Button",
			"fieldname": "add_to_contact_group",
			"width": 180
		},
		{
			"label": _("Contact"),
			"fieldname": "contact",
			"fieldtype": "Link",
			"options": "Contact",
			# "hidden": 1,
			"width": 180
		},
		{
			"label": _("First Name"),
			"fieldname": "first_name",
			"fieldtype": "Data",
			# "hidden": 1,
			"width": 180
		},
		{
			"label": _("Last Name"),
			"fieldname": "last_name",
			"fieldtype": "Data",
			# "hidden": 1,
			"width": 180
		},
		{
			"label": _("Email Address"),
			"fieldname": "email_id",
			"fieldtype": "Data",
			"options": "Email",
			# "hidden": 1,
			"width": 180
		},
		{
			"label": _("Contact Reference"),
			"fieldname": "contact_reference",
			"fieldtype": "Data",
			# "hidden": 1,
			"width": 180
		},

	]
	return columns


@frappe.whitelist()
def update_row_in_contact_set(contact, contact_row, contact_set):
	if not frappe.db.exists("Contact Set", contact_set):
		frappe.throw("Invalid Contact Set")

	contact_detail = frappe.db.get_values("Contact", contact, ["first_name" ,"last_name", "email_id"], as_dict=1)[0]
	contact_row_detail = frappe.db.get_values("Dynamic Link", {"parent": contact, "name": contact_row}, ["link_doctype" ,"link_name"], as_dict=1)[0]

	contact_set = frappe.get_doc("Contact Set", contact_set)

	contact_set.append("contact_set_contacts", {
		"contact": contact,
		"contact_row": contact_row,
		"first_name": contact_detail.get("first_name"),
		"last_name": contact_detail.get("last_name"),
		"email_id": contact_detail.get("email_id"),
		"link_doctype": contact_row_detail.get("link_doctype"),
		"link_name": contact_row_detail.get("link_name")
	})
	
	contact_set.save()
	frappe.msgprint(_("Added Contact to {0} ✅").format(frappe.get_desk_link("Contact Set", contact_set.name)))