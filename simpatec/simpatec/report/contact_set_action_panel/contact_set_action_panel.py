# Copyright (c) 2024, Phamos GmbH and contributors
# For license information, please see license.txt

import json
import frappe
from frappe import _
from frappe.utils import cstr, now, now_datetime, format_datetime
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
			cs.name as contact_set, csc.name as contact_set_row, csc.contact
		FROM `tabContact Set` cs
		LEFT JOIN `tabContact Set Contacts` csc
		ON csc.parent = cs.name 
		WHERE cs.name = %s and csc.parent IS NOT NULL ORDER BY csc.creation ASC""", (filters.get("contact_set")),
		as_dict=1,
	)
	status_collor_map = {"New": "purple", "In Work": "green", "Rejected": "red", "Opportunity": "blue"}

	for row in data:
		row_for_ui = get_row_for_ui(copy.copy(row))
		row_for_ui["emails"] = get_contact_info(row_for_ui.contact, "email")
		row_for_ui["phone_nos"] = get_contact_info(row_for_ui.contact, "phone")
		row_for_ui["last_action_on"] = cstr(row_for_ui["last_action_on"])
		row['action'] ='<button class="btn btn-primary btn-sm primary-action" onclick="contact_set_control_panel.open_dialog({0})">{1}</button>'.format(row_for_ui,  _("Action 📝"))
		if row.get("status"):
			row["status"] = '<span class="indicator-pill {0}"><span>{1}</span><span></span></span>'.format(status_collor_map.get(row["status"]), row["status"])

	return data


def get_row_for_ui(row):
	for key, value in row.items():
		if value is None:
			row[key] = "null"

	return row

def get_contact_info(contact, info_type):
	field_name = "email_id" if info_type == "email" else "phone"
	parentfield = "email_ids" if info_type == "email" else "phone_nos"
	data = frappe.db.sql(
		"""
		SELECT {field} FROM `tabContact {Type}`
		WHERE parent = %s and parenttype = "Contact" and parentfield = "{parentfield}" ORDER BY creation ASC""".format(field=field_name, parentfield=parentfield, Type=info_type.capitalize()),
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
			"width": 100
		},
		{
			"label": _("Status"),
			"fieldtype": "Data",
			"fieldname": "status",
			"width": 130
		},
		{
			"label": _("Last Action On"),
			"fieldtype": "Datetime",
			"fieldname": "last_action_on",
			"width": 130
		}
	]
	return columns


@frappe.whitelist()
def update_row_in_contact_set(contact_set, contact_set_row, notes=None, status=None):

	if not frappe.db.exists("Contact Set", contact_set):
		frappe.throw("Invalid Contact Set")


	contact_set = frappe.get_doc("Contact Set", contact_set)
	dirty = False
	for contact in contact_set.contact_set_contacts:
		if contact.name == contact_set_row:
			if status and status != contact.status:
				contact.status = status
				dirty = True
			if notes:
				contact.notes = notes
				dirty = True
	if dirty:
		for contact in contact_set.contact_set_contacts:
			if contact.name == contact_set_row:
				contact.last_action_on = now()

		contact_set.save()


@frappe.whitelist()
def get_row_log(contact_set, contact_set_row):
	row_log = []
	fields_for_log = ["status", "notes"]
	data_format = "{} HH:mm:ss".format(frappe.db.get_single_value("System Settings", "date_format"))
	versions = frappe.get_all("Version", filters={"ref_doctype": "Contact Set", "docname": contact_set}, fields=["data", "creation"], order_by="creation asc")
	for version in versions:
		data = json.loads(version.data)
		added = data["added"]
		row_changed = data["row_changed"]

		for row_ad in added:
			row_ad_table_fieldname = row_ad[0]
			row_ad_table_fielddata = (row_ad[1])
			if row_ad_table_fieldname == "contact_set_contacts" and row_ad_table_fielddata.get("name") == contact_set_row:
				log_dict = {
					"event": "Created On",
					"status": row_ad_table_fielddata.get("status"),
					"date": format_datetime(row_ad_table_fielddata.get("creation"), format_string=data_format)
				}
				row_log.append(log_dict)

		for row_ch in row_changed:
			if row_ch[2] == contact_set_row:
				row_change = row_ch[3]
				log_dict = {}
				fields_for_log_exist = False
				for d in row_change:
					log_field = d[0]
					old_data = d[1]
					new_data = d[2]

					if log_field in fields_for_log:
						fields_for_log_exist = True
						log_dict[log_field] = new_data

				if fields_for_log_exist:
					log_dict["event"] = "Updated On"
					log_dict["date"] = format_datetime(version.creation, format_string=data_format)
					row_log.append(log_dict)

	return row_log