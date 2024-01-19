# Copyright (c) 2024, Phamos GmbH and contributors
# For license information, please see license.txt

import json
import frappe
from frappe import _
from frappe.utils import cstr
import copy

def execute(filters=None):
	data = get_data(filters)
	columns = get_columns()
	return columns, data



def get_data(filters):
	if not filters.get("contact_set"):
		return

	data = frappe.db.sql(
		"""
		SELECT 
			cs.title, csc.first_name, csc.last_name, csc.status, csc.last_action_on,
			cs.name as contact_set, csc.name as contact_set_row, csc.contact, csc.notes
		FROM `tabContact Set` cs
		LEFT JOIN `tabContact Set Contacts` csc
		ON csc.parent = cs.name 
		WHERE cs.name = %s and csc.parent IS NOT NULL ORDER BY csc.creation ASC""", (filters.get("contact_set")),
		as_dict=1,
	)

	for row in data:
		row_for_ui = get_row_for_ui(copy.copy(row))
		row_for_ui['emails'] = get_contact_info(row_for_ui.contact, 'email')
		row_for_ui['phone_nos'] = get_contact_info(row_for_ui.contact, 'phone')
		row['action'] ='<button class="btn btn-sm" onclick="contact_set_control_panel.open_dialog({0})">{1}</button>'.format(row_for_ui,  _("Action"))
	
	return data


def get_row_for_ui(row):
	for key, value in row.items():
		if value is None:
			row[key] = 'null'

	return row

def get_contact_info(contact, info_type):
	if info_type not in ('email', 'phone'):
		raise frappe.throw("Invalid info_type. Use 'email' or 'phone'.")

	field_name = 'email_id' if info_type == 'email' else 'phone'
	parentfield = 'email_ids' if info_type == 'email' else 'phone_nos'
	data = frappe.db.sql(
		"""
		SELECT {field} FROM `tabContact {Type}`
		WHERE parent = %s and parenttype = 'Contact' and parentfield = '{parentfield}' ORDER BY creation ASC""".format(field=field_name, parentfield=parentfield, Type=info_type.capitalize()),
		(contact,),
		as_dict=1
	)
	return data


def get_columns():
	columns = [
		{
			"label": _("Title"),
			"fieldtype": "Data",
			"fieldname": "title",
			"width": 180
		},
		{
			"label": _("First Name"),
			"fieldtype": "Data",
			"fieldname": "first_name",
			"width": 180
		},
		{
			"label": _("Last Name"),
			"fieldtype": "Data",
			"fieldname": "last_name",
			"width": 180
		},
		{
			"label": _("Action"),
			"fieldtype": "Button",
			"fieldname": "action",
			"width": 180
		},
		{
			"label": _("Status"),
			"fieldtype": "Data",
			"fieldname": "status",
			"width": 180
		},
		{
			"label": _("Last Action On"),
			"fieldtype": "Datetime",
			"fieldname": "last_action_on",
			"width": 180
		}
	]
	return columns


@frappe.whitelist()
def update_row_in_contact_set(contact_set, contact_set_row, data={}):
	if isinstance(data, str):
		data = json.loads(data)

	if not frappe.db.exists("Contact Set", contact_set):
		frappe.throw("Invalid Contact Set")


	contact_set = frappe.get_doc("Contact Set", contact_set)
	dirty = False
	row_idx = None
	for contact in contact_set.contact_set_contacts:
		if contact.name == contact_set_row:
			row_idx = contact.idx
			if data.get("status") != contact.status:
				contact.status = data.get("status")
				dirty = True
			if data.get("notes") != contact.notes:
				contact.notes = data.get("notes")
				dirty = True
	if dirty:
		contact_set.save()
