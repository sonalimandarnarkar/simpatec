import frappe


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def custom_contact_query(doctype, txt, searchfield, start, page_len, filters=None):
    f = [["name", "like", "%" + txt + "%"]]
    if filters:
        f.extend(filters)
    filters = f

    contacts = frappe.db.get_list("Contact", 
                filters=filters, 
                limit=page_len, 
                fields=["name as value", "email_id as description"], as_list=True)
    return contacts