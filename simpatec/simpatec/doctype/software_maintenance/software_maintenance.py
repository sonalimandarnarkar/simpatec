# Copyright (c) 2023, Phamos GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

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
