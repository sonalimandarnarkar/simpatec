# Copyright (c) 2024, Phamos GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import now


@frappe.whitelist()
def execute(filters=None):
	data = get_data(filters)
	columns = get_columns()
	return columns, data


def get_data(filters):
	data = []
	contacts = frappe.db.get_list("Contact", fields="name", filters=filters)
	if contacts:
		contacts = tuple(contact.name for contact in contacts)
		data = frappe.db.sql(
			"""
			select c.name as contact, dl.name as contact_row, c.first_name, c.last_name, c.email_id, 
			dl.link_doctype as ref_type, dl.name as contact_row_reference, dl.link_name as ref_name, dl.link_title as ref_title
			from
				`tabContact` c, `tabDynamic Link` dl
			where dl.parent = c.name and c.name in (%s)""" % (",".join(["%s"] * len(contacts))), contacts, as_dict=1,
		)

	for d in data:
		ref_title = d.get('ref_title') if d.get('ref_title') == d.get('ref_name') else "{0}: {1}".format(d.get('ref_name'), d.get('ref_title'))
		d['contact_reference'] = '<a href="/app/Form/{0}/{1}" >{2} ({0})</a>'.format(d.get('ref_type'), d.get('ref_name'), ref_title)
		d['add_to_contact_group'] ="""
			<div>
				<button class="btn btn-sm" onclick="contact_register.open_dialog({0}, {1})">{2}</button>
			</div>
		""".format("'" + d.contact + "'", "'" + d.contact_row + "'",  _("Add to Contact Set"))
		d['check_bulk_select'] ='<input class="bulk-select-contact-set" data-contact={0} data-contact-row={1} type="checkbox" id={1} onclick="update_bulk_list({0}, {1})">'.format("'" + d.contact + "'", "'" + d.contact_row + "'")
	
	return data


def get_columns():
	columns = [
		{
			"label": _("Select"),
			"fieldname": "check_bulk_select",
			"fieldtype": "Button",
			"width": 70
		},
		{
			"label": _("Action"),
			"fieldtype": "Button",
			"fieldname": "add_to_contact_group",
			"width": 280
		},
		{
			"label": _("Contact"),
			"fieldname": "contact",
			"fieldtype": "Link",
			"options": "Contact",
			"width": 180
		},
		{
			"label": _("First Name"),
			"fieldname": "first_name",
			"fieldtype": "Data",
			"width": 180
		},
		{
			"label": _("Last Name"),
			"fieldname": "last_name",
			"fieldtype": "Data",
			"width": 180
		},
		{
			"label": _("Email Address"),
			"fieldname": "email_address",
			"fieldtype": "Data",
			"options": "Email",
			"width": 180
		},
		{
			"label": _("Contact Reference"),
			"fieldname": "contact_reference",
			"fieldtype": "Data",
			"width": 250
		}
	]
	return columns


@frappe.whitelist()
def update_row_in_contact_set(contact, contact_row, contact_set, show_success_msg=True):
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
		"link_name": contact_row_detail.get("link_name"),
		"status": "New",
		"last_action_on": now()
	})
	
	contact_set.save()
	if show_success_msg:
		frappe.msgprint(_("Added Contact to {0} ✅").format(frappe.get_desk_link("Contact Set", contact_set.name)))


@frappe.whitelist()
def bulk_update_row_in_contact_set(contact_set, bulk_update_rows):
	bulk_update_rows = frappe.parse_json(bulk_update_rows)
	failed = []
	for i, d in enumerate(bulk_update_rows, 1):
		if d.get("contact") and d.get("contact_row"):
			try:
				update_row_in_contact_set(d.get("contact"), d.get("contact_row"), contact_set, show_success_msg=False)
				frappe.db.commit()
				show_progress(bulk_update_rows, "Updating Contact Set", i, d)

			except Exception:
				failed.append(d)
				frappe.db.rollback()

	return failed


def show_progress(docnames, message, i, description):
	n = len(docnames)
	if n >= 10:
		frappe.publish_progress(float(i) * 100 / n, title=message, description=description)
