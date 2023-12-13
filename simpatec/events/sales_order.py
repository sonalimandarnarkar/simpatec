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
def create_followup_software_maintenance_sales_order(date=None):
	if not date:
		date = today()
	software_maintenance_list = frappe.get_all('Software Maintenance', filters={'performance_period_end': ("=", date)})
	for software_maintenance in software_maintenance_list:
		make_sales_order(software_maintenance)
		frappe.db.commit()


def make_sales_order(software_maintenance):
	software_maintenance = frappe.get_doc("Software Maintenance", software_maintenance.name)

	sales_order = frappe.new_doc("Sales Order")
	sales_order.customer_subsidiary = software_maintenance.customer_subsidiary
	sales_order.performance_period_start = add_days(software_maintenance.performance_period_end, -cint(software_maintenance.lead_time)) 
	sales_order.performance_period_end =  add_days(software_maintenance.performance_period_end, 365)
	sales_order.software_maintenance = software_maintenance.name
	sales_order.item_group = software_maintenance.item_group
	sales_order.customer = software_maintenance.customer
	sales_order.sales_order_type = "Follow Up Maintenance"
	sales_order.ihr_ansprechpartner = "HR-EMP-00001"
	sales_order.transaction_date = today()
	sales_order.order_type = "Sales"

	for item in software_maintenance.items:
		sales_order.append("items", {
			"item_code": item.item_code,
			"item_name": item.item_name,
			"description": item.description,
			"conversion_factor": item.conversion_factor,
			"qty": item.qty,
			"rate": item.rate,
			"uom": item.uom,
			"delivery_date": sales_order.transaction_date
		})

	sales_order.insert()