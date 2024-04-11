import frappe

@frappe.whitelist()
def validate(doc, handler=None):
    """"""
    supplier_lang = frappe.db.get_value('Supplier',doc.supplier,'language')
    doc.language = supplier_lang
    
    for lang in doc.items:
        lang.item_language = supplier_lang
        ##print(lang.description)

@frappe.whitelist()
def on_submit(doc, handler=None):
    update_clearance_amount_in_sales_order(doc)

def update_clearance_amount_in_sales_order(self):
    """Update Clearance Amount in Sales Order"""
    for item in self.items:
        if item.sales_order:
            so = frappe.get_doc("Sales Order", item.sales_order)
            is_eligable_for_clearance = so.eligable_for_clearance
            internal_clearance_details = so.internal_clearance_details
            if is_eligable_for_clearance:
                if internal_clearance_details is not None and internal_clearance_details != "":
                    internal_commision_rate = frappe.db.get_value("Internal Clearance Details", internal_clearance_details, "clearance_rate") or 0
                    """Clearance Comission (Z)
                    Sales Order net amount (Y)
                    Purchase Order net amount (X)
                    Clearance Amount = ((Y) - (X)) * (1-(Z))"""

                    po_total_amount = self.total
                    so_margin_amount = so.total - self.total
                    so_margin_percent = ((so.total - self.total)/so.total) * 100
                    clearance_amount = (so.total - self.total) * (internal_commision_rate/100)
                    frappe.db.set_value(so.doctype, so.name, "po_total", po_total_amount)
                    frappe.db.set_value(so.doctype, so.name, "so_margin", so_margin_amount)
                    frappe.db.set_value(so.doctype, so.name, "so_margin_percent", so_margin_percent)
                    frappe.db.set_value(so.doctype, so.name, "clearance_amount", clearance_amount)