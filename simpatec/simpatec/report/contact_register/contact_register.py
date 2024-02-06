# Copyright (c) 2024, Phamos GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import now, cstr
from frappe.handler import execute_cmd

@frappe.whitelist()
def execute(filters=None, limit=100):
	filters = frappe.parse_json(filters)
	if not filters:
		filters = []

	if not limit:
		limit = 100

	filters.append(["Dynamic Link","name","is","set",0])
	data, total_count = get_data(filters, limit=limit)
	columns = get_columns()
	return columns, data, total_count


def get_data(filters, limit=100):
	data = []
	frappe.local.form_dict = frappe._dict({"doctype": "Contact", "fields": ["name"], "filters": filters})
	total_count = len(execute_cmd("frappe.desk.reportview.get_list"))

	fields = [
		"`tabContact`.`name` as contact","`tabContact`.`first_name`", "`tabContact`.`last_name`", "`tabContact`.`email_id` as email_address",
		 "`tabDynamic Link`.`name` as contact_row", "`tabDynamic Link`.`link_doctype` as ref_type", "`tabDynamic Link`.`link_name` as ref_name",
		 "`tabDynamic Link`.`link_title` as ref_title"
	]
	frappe.local.form_dict = frappe._dict({
		"doctype": "Contact", "fields": fields, "filters": filters, "limit": limit, "order_by": "`tabContact`.`modified` asc",
		"as_list": 0, "debug": 1
	})
	data = execute_cmd("frappe.desk.reportview.get_list")
	for d in data:
		ref_title = d.get('ref_title') if d.get('ref_title') == d.get('ref_name') else "{0}: {1}".format(d.get('ref_name'), d.get('ref_title'))
		d['contact_reference'] = '<a href="/app/Form/{0}/{1}" >{2} ({0})</a>'.format(d.get('ref_type'), d.get('ref_name'), ref_title)
		d['add_to_contact_group'] ="""
			<div>
				<button class="btn btn-sm" onclick="contact_register.open_dialog({0}, {1})">{2}</button>
			</div>
		""".format("'" + d.contact + "'", "'" + d.contact_row + "'",  _("Add to Contact Set"))
		d['check_bulk_select'] ='<input class="bulk-select-contact-set" data-contact={0} data-contact-row={1} type="checkbox" id={1} onclick="update_bulk_list({0}, {1})">'.format("'" + d.contact + "'", "'" + d.contact_row + "'")

	return data, "{0} of {1}".format(len(data), total_count)


def get_columns():
	columns = [
		{
			"label": _('<input class="bulk-select-all" type="checkbox" onclick="bulk_select_all()" />'),
			"fieldname": "check_bulk_select",
			"fieldtype": "Button",
			"width": 70
		},
		{
			"label": _("Action"),
			"fieldtype": "Button",
			"fieldname": "add_to_contact_group",
			"width": 150
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
	contact_row_detail = frappe.db.get_values("Dynamic Link", {"parent": contact, "name": contact_row}, ["link_doctype" ,"link_name", "link_title"], as_dict=1)[0]

	contact_set = frappe.get_doc("Contact Set", contact_set)

	contact_set.append("contact_set_contacts", {
		"contact": contact,
		"contact_row": contact_row,
		"first_name": contact_detail.get("first_name"),
		"last_name": contact_detail.get("last_name"),
		"email_id": contact_detail.get("email_id"),
		"link_doctype": contact_row_detail.get("link_doctype"),
		"link_name": contact_row_detail.get("link_name"),
		"link_title": contact_row_detail.get("link_title"),
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
