# Copyright (c) 2024, Phamos GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class ContactSet(Document):
	def validate(self):
		self.validate_unique_item_code_and_group()

	def validate_unique_item_code_and_group(self):
		contact_combinations = set()

		for contact in self.contact_set_contacts:
			if contact.contact and contact.contact_row:
				combination = (contact.contact, contact.contact_row)
				if combination in contact_combinations:
					frappe.throw(_("This row already exist in {0}").format(frappe.get_desk_link("Contact Set", self.name)))
				contact_combinations.add(combination)