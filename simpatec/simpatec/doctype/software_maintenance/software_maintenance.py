# Copyright (c) 2023, Phamos GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class SoftwareMaintenance(Document):
	def on_update(self):
		self.update_sales_order()

	def update_sales_order(self):
		if self.sales_order:
			software_maintenance = frappe.get_cached_value('Sales Order', self.sales_order, 'software_maintenance')
			if software_maintenance and software_maintenance != self.name:
				frappe.throw(_('Software Maintenance already exist for {0}').format(frappe.get_desk_link("Sales Order", self.sales_order)))
			
			if not software_maintenance:
				frappe.db.set_value('Sales Order', self.sales_order, 'software_maintenance', self.name)
				frappe.msgprint(_('"Software Maintenance" field updated in {0}').format(frappe.get_desk_link("Sales Order", self.sales_order)))
