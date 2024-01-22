import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def after_migrate():
	create_custom_fields(get_custom_fields())


def before_uninstall():
	delete_custom_fields(get_custom_fields())


def delete_custom_fields(custom_fields):
	for doctype, fields in custom_fields.items():
		for field in fields:
			custom_field_name = frappe.db.get_value(
				"Custom Field", dict(dt=doctype, fieldname=field.get("fieldname"))
			)
			if custom_field_name:
				frappe.delete_doc("Custom Field", custom_field_name)

		frappe.clear_cache(doctype=doctype)


def get_custom_fields():
	custom_fields_customer = [
		{
			"label": "SimpaTec",
			"fieldname": "simpatec_section",
			"fieldtype": "Section Break",
		},
		{
			"label": "Is Supplier",
			"fieldname": "is_supplier",
			"fieldtype": "Check",
			"insert_after": "simpatec_section"
		},
		{
			"label": "Ist Vertriebspartner",
			"fieldname": "ist_vertriebspartner",
			"fieldtype": "Check",
			"insert_after": "is_supplier"
		},
		{
			"label": "Vertriebs_partner",
			"fieldname": "vertriebs_partner",
			"fieldtype": "Link",
			"options": "Customer",
			"insert_after": "ist_vertriebspartner"
		},
		{
			"label": "Supplier",
			"fieldname": "supplier",
			"fieldtype": "Link",
			"options": "Supplier",
			"insert_after": "vertriebs_partner"
		},
		{
			"label": "Supplier Number",
			"fieldname": "supplier_number",
			"fieldtype": "Data",
			"insert_after": "supplier"
		},
		{
			"label": "Additional Information",
			"fieldname": "additional_information",
			"fieldtype": "Column Break",
			"insert_after": "supplier_number"
		},
		{
			"label": "Mutter",
			"fieldname": "mutter",
			"fieldtype": "Link",
			"options": "Customer",
			"insert_after": "additional_information"
		},
		{
			"label": "Rechnungsversand",
			"fieldname": "rechnungsversand",
			"fieldtype": "Select",
			"options": "\nE-Mail\npostalisch",
			"insert_after": "mutter"	
		},
		{
			"label": "Zahlungsschwierigkeiten",
			"fieldname": "zahlungsschwierigkeiten",
			"fieldtype": "Select",
			"options": 'keine\nJa "Achtung"\n!!! STOPP keine Verkäufe mehr !!!',
			"insert_after": "rechnungsversand"	
		},
		{
			"label": "Customer since",
			"fieldname": "customer_since",
			"fieldtype": "Date",
			"insert_after": "zahlungsschwierigkeiten"	
		}
	]


	custom_fields_so = [
		{
			"label": "SimpaTec",
			"fieldname": "simpatec_section",
			"fieldtype": "Section Break",
		},
		{
			"label": "Sales Order Type",
			"fieldname": "sales_order_type",
			"fieldtype": "Select",
			"options": "\nFirst Sale\nFollow Up Maintenance\nRTO\nSubscription Annual\nOther",
			"default": "",
			"insert_after": "simpatec_section"
		},
		{
			"label": "Item Group",
			"fieldname": "item_group",
			"fieldtype": "Link",
			"options": "Item Group",
			"insert_after": "sales_order_type"
		},
		{
			"label": "Performance Period Start",
			"fieldname": "performance_period_start",
			"fieldtype": "Date",
			"description": "Muss gefüllt werden wenn Wartungspositionen in Auftrag gehen.",
			"insert_after": "item_group",
		},
		{
			"fieldname": "column_break_fdgxg",
			"fieldtype": "Column Break",
			"insert_after": "performance_period_start",
		},
		{
			"label": "UID",
			"fieldname": "uid",
			"fieldtype": "Data",
			"insert_after": "column_break_fdgxg"
		},
		{
			"label": "Customer Subsidiary",
			"fieldname": "customer_subsidiary",
			"fieldtype": "Link",
			"options": "Customer Subsidiary",
			"reqd":1,
			"insert_after": "uid"
		},
		{
			"label": "Performance Period End",
			"fieldname": "performance_period_end",
			"fieldtype": "Date",
			"description": "Muss gefüllt werden wenn Wartungspositionen in Auftrag gehen.",
			"insert_after": "customer_subsidiary",
		},
		{
			"label": "Assigned to",
			"fieldname": "assigned_to",
			"fieldtype": "Link",
			"options": "User",
			"fetch_from": "customer_subsidiary.assigned_to",
			"fetch_if_empty":1,
			"insert_after": "performance_period_end"
		},
		{
			"label": "Ihr Ansprechpartner",
			"fieldname": "ihr_ansprechpartner",
			"fieldtype": "Link",
			"options": "Employee",
			"reqd":1,
			"insert_after": "assigned_to"
		},
	]

	custom_fields_soi = [
		{
			"label": "Item Language",
			"fieldname": "item_language",
			"fieldtype": "Link",
			"options": "Language",
			"reqd":1,
			"insert_after": "col_break1"
		},
		{
			"label": "Start Date",
			"fieldname": "start_date",
			"fieldtype": "Date",
			"insert_after": "item_language",
		},
		{
			"label": "End Date",
			"fieldname": "end_date",
			"fieldtype": "Date",
			"insert_after": "start_date",
		}
	]

	return {
		"Customer": custom_fields_customer,
		"Sales Order": custom_fields_so,
		"Sales Order Item": custom_fields_soi
	}
