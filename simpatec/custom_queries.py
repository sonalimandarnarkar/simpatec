import frappe


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def custom_contact_query(doctype, txt, searchfield, start, page_len, filters=None):
    print("custom_contact_query")
    contacts = frappe.db.get_list("Contact", 
                filters=[["name", "like", "%" + txt + "%"]], 
                limit=page_len, 
                fields=["name as value", "email_id as description"], as_list=True)
    return contacts