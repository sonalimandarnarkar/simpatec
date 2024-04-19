import frappe
from frappe import _
from frappe.utils import cint, cstr, flt, add_days, add_years, today, getdate
from frappe.model.mapper import get_mapped_doc
from datetime import date, timedelta


@frappe.whitelist()
def validate(doc, handler=None):
	if doc.sales_order_type == "Internal Clearance":
		doc.eligable_for_clearance = 0
		doc.internal_clearance_details = ""
	elif doc.eligable_for_clearance:
		doc.sales_order_clearances = []

	validate_duplicate_linked_internal_clearance(doc)


@frappe.whitelist()
def validate_duplicate_linked_internal_clearance(doc):
	linked_so = []
	if doc.sales_order_type == "Internal Clearance":
		for so in doc.sales_order_clearances:
			so_clearances = frappe.get_all("Sales Order Clearances", filters={
					"sales_order":so.sales_order, 
					"parent":["!=", doc.name],
					"docstatus": ["!=", 2]
				})
			if len(so_clearances) > 0:
				linked_so.append(so.sales_order)

	if len(linked_so) > 0:
		linked_so = " <br>".join(linked_so)
		frappe.throw("Cannot be linked because these Sales Order are already linked in Different Clearances <br> {0}".format(linked_so))



@frappe.whitelist()
def reset_internal_clearance_status(doc, handler=None):
	if doc.sales_order_type == "Internal Clearance":
		for so in doc.sales_order_clearances:
			so_doc = frappe.get_doc("Sales Order", so.sales_order)
			if so_doc.clearance_status == "Cleared":
				frappe.db.set_value(so_doc.doctype, so_doc.name, "clearance_status", "Not Cleared")


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

@frappe.whitelist()
def update_internal_clearance_status(doc, handler=None):
	if doc.sales_order_type == "Internal Clearance":
		for item in doc.items:
			internal_so = doc.sales_order_clearances[item.idx - 1].get("sales_order")
			frappe.db.set_value(doc.doctype, internal_so, "clearance_status", "Cleared")


def update_software_maintenance(doc, method=None):
	if doc.get("software_maintenance"):
		software_maintenance = frappe.get_doc("Software Maintenance", doc.software_maintenance)
		if (doc.performance_period_start is not None and doc.performance_period_start != "") and (doc.performance_period_end is not None and doc.performance_period_end != ""):
			if software_maintenance.performance_period_start != doc.performance_period_start:
				software_maintenance.performance_period_start = doc.performance_period_start
			if software_maintenance.performance_period_end != doc.performance_period_end:
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
				"item_language": item.item_language,
				"rate": item.rate,
				"qty": item.qty,
				"uom": item.uom
			})

		software_maintenance.save()


def create_followup_software_maintenance_sales_order(date=None):
	if not date:
		date = today()

	software_maintenance_list = frappe.db.sql("""
		SELECT name 
		FROM `tabSoftware Maintenance`
		WHERE DATE_SUB(performance_period_end, INTERVAL lead_time DAY) = %s
	""", date, as_dict=1)

	for software_maintenance in software_maintenance_list:
		try:
			make_sales_order(software_maintenance.name)
		except Exception as e:
			error_message = frappe.get_traceback()+"{0}\n".format(str(e))
			frappe.log_error(error_message, 'Error occured While automatically Software Maintenance Sales Order for {0}'.format(software_maintenance))
		finally:
			frappe.db.commit()


@frappe.whitelist()
def make_sales_order(software_maintenance, is_background_job=True):
	software_maintenance = frappe.get_doc("Software Maintenance", software_maintenance)
	if not software_maintenance.assign_to:
		frappe.throw(_("Please set 'Assign to' in Software maintenance '{0}'").format(software_maintenance.name))

	employee =  frappe.get_cached_value('Employee', {'user_id': software_maintenance.assign_to}, 'name')
	if not employee:
		frappe.throw(_("User {0} not set in Employee").format(software_maintenance.assign_to))
	old_start_date = software_maintenance.performance_period_start
	performance_period_start = add_days(software_maintenance.performance_period_end, 1)
	performance_period_end = add_years(performance_period_start, software_maintenance.maintenance_duration) - timedelta(days=1)
	total_days = getdate(performance_period_end) - getdate(performance_period_start)

	days_diff = total_days.days%365
	if days_diff != 0:
		_performance_period_end = add_days(performance_period_end, -days_diff)
		total_days = getdate(_performance_period_end) - getdate(performance_period_start)

	transaction_date = add_days(performance_period_end, -cint(software_maintenance.lead_time))
	sales_order = frappe.new_doc("Sales Order")
	sales_order.customer_subsidiary = software_maintenance.customer_subsidiary
	sales_order.performance_period_start = performance_period_start
	sales_order.performance_period_end = performance_period_end
	sales_order.software_maintenance = software_maintenance.name
	sales_order.item_group = software_maintenance.item_group
	sales_order.customer = software_maintenance.customer
	sales_order.sales_order_type = "Follow Up Maintenance"
	sales_order.ihr_ansprechpartner = employee
	sales_order.transaction_date = transaction_date
	sales_order.order_type = "Sales"

	for item in software_maintenance.items:
		start_date = performance_period_start
		item_rate = item.rate
		if item.start_date != old_start_date:
			per_day_rate = item.rate / 365
			start_date = item.end_date
			d0 = start_date
			d1 = performance_period_end
			delta = d1 - d0
			days_remaining = delta.days
			total_remaining_item_rate = days_remaining * per_day_rate
			item_rate = total_remaining_item_rate

		sales_order.append("items", {
			"item_code": item.item_code,
			"item_name": item.item_name,
			"description": item.description,
			"conversion_factor": item.conversion_factor,
			"qty": item.qty,
			"rate": item_rate,
			"uom": item.uom,
			"item_language": item.item_language,
			"delivery_date": sales_order.transaction_date,
			"start_date": start_date,
			"end_date": performance_period_end
		})

	sales_order.insert()

	if not cint(is_background_job):
		frappe.msgprint("Maintenance Duration (Years): {}".format(software_maintenance.maintenance_duration))
		frappe.msgprint("Maintenance Duration (Days): {}".format(total_days.days))
		frappe.msgprint(_("New {} Created").format(frappe.get_desk_link("Sales Order", sales_order.name)))