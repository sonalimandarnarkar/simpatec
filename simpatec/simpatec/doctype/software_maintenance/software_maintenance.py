# Copyright (c) 2023, Phamos GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, add_days, add_years, getdate
from datetime import timedelta

class SoftwareMaintenance(Document):

	def before_save(self):
		if self.is_new():
			self.new_doc = True

	def on_update(self):
		self.update_sales_order()

	def update_sales_order(self):
		if self.sales_order and not self.is_new():
			software_maintenance = frappe.get_cached_value('Sales Order', self.sales_order, 'software_maintenance')
			if software_maintenance and software_maintenance != self.name:
				frappe.throw(_('Software Maintenance already exist for {0}').format(frappe.get_desk_link("Sales Order", self.sales_order)))
			
			if not software_maintenance:
				frappe.db.set_value('Sales Order', self.sales_order, 'software_maintenance', self.name)
				frappe.msgprint(_("This Software Maintenance has been updated in the respective link field in Sales Order {0} ℹ️".format(frappe.get_desk_link("Sales Order", self.sales_order))))


@frappe.whitelist()
def make_reoccuring_sales_order(software_maintenance, is_background_job=True):
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
	sales_order.sales_order_type = "Reoccuring Maintenance"
	sales_order.ihr_ansprechpartner = employee
	sales_order.transaction_date = transaction_date
	sales_order.order_type = "Sales"

	for item in software_maintenance.items:
		sales_order.append("items", {
			"item_code": item.item_code,
			"item_name": item.item_name,
			"description": item.description,
			"conversion_factor": item.conversion_factor,
			"qty": item.qty,
			"rate": item.rate,
			"reoccurring_maintenance_amount": item.reoccurring_maintenance_amount,
			"uom": item.uom,
			"item_language": item.item_language,
			"delivery_date": sales_order.transaction_date,
			"start_date": item.start_date,
			"end_date": item.end_date,
			"einkaufspreis": item.einkaufspreis
		})

	sales_order.insert()

	if not cint(is_background_job):
		frappe.msgprint("Maintenance Duration (Years): {}".format(software_maintenance.maintenance_duration))
		frappe.msgprint("Maintenance Duration (Days): {}".format(total_days.days))
		frappe.msgprint(_("New {} Created").format(frappe.get_desk_link("Sales Order", sales_order.name)))