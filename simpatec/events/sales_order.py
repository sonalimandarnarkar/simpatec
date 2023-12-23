import frappe
from frappe.utils import cint, cint, flt, add_days, add_years, today
from frappe.model.mapper import get_mapped_doc


@frappe.whitelist()
def make_software_maintenance(source_name, target_doc=None):
	def postprocess(source, doc):
		if source.sales_order_type == "First Sale":
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
			"Sales Order Item": {
				"doctype": "Software Maintenance Item",
			},
		},
		target_doc,
		postprocess,
	)

	return doc


def update_software_maintenance(doc, method=None):
	if doc.software_maintenance:
		software_maintenance = frappe.get_doc("Software Maintenance", doc.software_maintenance)
		software_maintenance.performance_period_start = doc.performance_period_start
		software_maintenance.performance_period_end = doc.performance_period_end
		software_maintenance.sale_order = doc.name
		for item in doc.items:
			software_maintenance.append("items", {
				"item_code": item.item_code,
				"item_name": item.item_name,
				"description": item.description,
				"start_date": item.start_date,
				"end_date": item.end_date,
				"price_list_rate": item.price_list_rate,
				"conversion_factor": item.conversion_factor,
				"rate": item.rate,
				"qty": item.qty,
				"uom": item.uom
			})

		software_maintenance.save()


def create_followup_software_maintenance_sales_order(date=None):
	if not date:
		date = today()
	software_maintenance_list = frappe.get_all('Software Maintenance', filters={'performance_period_end': ("=", date)})
	for software_maintenance in software_maintenance_list:
		try:
			make_sales_order(software_maintenance)
		except Exception as e:
			error_message = frappe.get_traceback()+"{0}\n".format(str(e))
			frappe.log_error(error_message, 'Error occured While automatically Software Maintenance Sales Order for {0}'.format(software_maintenance))
		finally:
			frappe.db.commit()


def make_sales_order(software_maintenance):
	software_maintenance = frappe.get_doc("Software Maintenance", software_maintenance.name)

	sales_order = frappe.new_doc("Sales Order")
	sales_order.customer_subsidiary = software_maintenance.customer_subsidiary
	sales_order.performance_period_start = add_days(software_maintenance.performance_period_end, software_maintenance.start_after_days)
	sales_order.performance_period_end = add_years(software_maintenance.performance_period_end, software_maintenance.maintenance_duration)
	sales_order.software_maintenance = software_maintenance.name
	sales_order.item_group = software_maintenance.item_group
	sales_order.customer = software_maintenance.customer
	sales_order.sales_order_type = "Follow Up Maintenance"
	sales_order.ihr_ansprechpartner = software_maintenance.ihr_ansprechpartner #new field in software maintenance
	sales_order.transaction_date = add_days(software_maintenance.performance_period_end, -cint(software_maintenance.lead_time))
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