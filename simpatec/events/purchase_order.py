import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def validate(doc, handler=None):
    """"""
    supplier_lang = frappe.db.get_value('Supplier',doc.supplier,'language')
    doc.language = supplier_lang
    
    for lang in doc.items:
        lang.item_language = supplier_lang
        ##print(lang.description)