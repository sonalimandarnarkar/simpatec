import frappe
from frappe.model.mapper import get_mapped_doc



@frappe.whitelist()
def make_software_maintenance(source_name, target_doc=None):
	def postprocess(source, doc):
		doc.first_sale_on = source.transaction_date
		doc.assign_to = source.assigned_to

	doc = get_mapped_doc(
		"Sales Order",
		source_name,
		{
			"Sales Order": {
				"doctype": "Software Maintenance",
				"field_map": {
					"name": "sales_order",
				},
			},
		},
		target_doc,
		postprocess,
	)

	return doc