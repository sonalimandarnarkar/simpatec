import json
import frappe
from frappe import _
from frappe.utils import cint, cstr, flt, add_days, add_years, today, getdate
from frappe.model.mapper import get_mapped_doc
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
from six import string_types

@frappe.whitelist()
def make_quotation(source_name: str, target_doc=None):
	return _make_quotation(source_name, target_doc)


def _make_quotation(source_name, target_doc=None, ignore_permissions=False):


	def set_missing_values(source, target):

		target.run_method("calculate_taxes_and_totals")

	doclist = get_mapped_doc(
		"Quotation",
		source_name,
		{
			"Quotation": {"doctype": "Quotation"},
			"Quotation Item": {
				"doctype": "Quotation Item",
				"field_map": {
					"parent": "prevdoc_docname",
					"parenttype": "prevdoc_doctype",
				},
			},
		},
		target_doc,
		set_missing_values,
		ignore_permissions=ignore_permissions,
	)

	return doclist
