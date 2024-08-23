# Copyright (c) 2024, Phamos GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import timedelta
from frappe.utils import now

class SimpaTecSettings(Document):
    @frappe.whitelist()
    def update_item_details(self):
        try:
            updated_record_ids_sm = []
            # Update item descriptions data from old field id_xx to new field item_description_xx
            
            # SOFTWARE MAINTENANCE ITEM
            # UPDATE DESCRIPTIONS
            records_to_update_sm = frappe.db.sql("""SELECT `name`, parent, item_language 
                    FROM `tabSoftware Maintenance Item`
                    WHERE (`item_description_en` IS NULL 
                        OR `item_description_en` = ''
                        OR `item_description_en` LIKE '%<div class="ql-editor read-mode"><p><br></p></div>%') or (`item_description_fr` IS NULL 
                        OR `item_description_fr` = ''
                        OR `item_description_fr` LIKE '%<div class="ql-editor read-mode"><p><br></p></div>%') or (`item_description_de` IS NULL 
                        OR `item_description_de` = ''
                        OR `item_description_de` LIKE '%<div class="ql-editor read-mode"><p><br></p></div>%') or 
                        (`item_name_en` IS NULL OR `item_name_en` = '') or 
                        (`item_name_fr` IS NULL OR `item_name_fr` = '') or 
                        (`item_name_de` IS NULL OR `item_name_de` = '')
            """, as_dict=True)
            # The list of IDs of the updated records
            updated_record_ids_sm += [f"'{record['parent']}'" for record in records_to_update_sm]
            
            frappe.db.sql("""UPDATE `tabSoftware Maintenance Item`
                                    SET `item_description_en` = 
                                        CASE
                                            -- If `item_description_en` is null, empty, or contains the specific HTML pattern
                                            WHEN `item_description_en` IS NULL 
                                                OR `item_description_en` = ''	
                                                OR `item_description_en` LIKE '%<div class="ql-editor read-mode"><p><br></p></div>%'
                                            THEN 
                                                -- If `id_en` is null, empty, or contains the specific HTML pattern
                                                CASE 
                                                    WHEN `id_en` IS NULL 
                                                        OR `id_en` = '' 
                                                        OR `id_en` LIKE '%<div class="ql-editor read-mode"><p><br></p></div>%'
                                                    THEN `description` -- If `id_en` also doesn't have valid content, use `description`
                                                    ELSE `id_en` -- Otherwise, use `id_en`
                                                END
                                            ELSE `item_description_en` -- If `item_description_en` does not match the conditions, do nothing
                                        END""")
            frappe.db.sql("""UPDATE `tabSoftware Maintenance Item`
                                    SET `item_description_fr` = 
                                        CASE
                                            -- If `item_description_fr` is null, empty, or contains the specific HTML pattern
                                            WHEN `item_description_fr` IS NULL 
                                                OR `item_description_fr` = ''	
                                                OR `item_description_fr` LIKE '%<div class="ql-editor read-mode"><p><br></p></div>%'
                                            THEN 
                                                -- If `id_fr` is null, empty, or contains the specific HTML pattern
                                                CASE 
                                                    WHEN `id_fr` IS NULL 
                                                        OR `id_fr` = '' 
                                                        OR `id_fr` LIKE '%<div class="ql-editor read-mode"><p><br></p></div>%'
                                                    THEN `description` -- If `id_fr` also doesn't have valid content, use `description`
                                                    ELSE `id_fr` -- Otherwise, use `id_fr`
                                                END
                                            ELSE `item_description_fr` -- If `item_description_fr` does not match the conditions, do nothing
                                        END""")
            
            frappe.db.sql("""UPDATE `tabSoftware Maintenance Item`
                                    SET `item_description_de` = 
                                        CASE
                                            -- If `item_description_de` is null, empty, or contains the specific HTML pattern
                                            WHEN `item_description_de` IS NULL 
                                                OR `item_description_de` = ''	
                                                OR `item_description_de` LIKE '%<div class="ql-editor read-mode"><p><br></p></div>%'
                                            THEN 
                                                -- If `id_de` is null, empty, or contains the specific HTML pattern
                                                CASE 
                                                    WHEN `id_de` IS NULL 
                                                        OR `id_de` = '' 
                                                        OR `id_de` LIKE '%<div class="ql-editor read-mode"><p><br></p></div>%'
                                                    THEN `description` -- If `id_de` also doesn't have valid content, use `description`
                                                    ELSE `id_de` -- Otherwise, use `id_de`
                                                END
                                            ELSE `item_description_de` -- If `item_description_de` does not match the conditions, do nothing
                                        END""")
            
            # UPDATE ITEM NAMES
            frappe.db.sql("update `tabSoftware Maintenance Item` set `item_name_en` = `item_name` where (`item_name_en` IS NULL OR `item_name_en` = '')")
            frappe.db.sql("update `tabSoftware Maintenance Item` set `item_name_de` = `item_name` where (`item_name_de` IS NULL OR `item_name_de` = '')")
            frappe.db.sql("update `tabSoftware Maintenance Item` set `item_name_fr` = `item_name` where (`item_name_fr` IS NULL OR `item_name_fr` = '')")
            
            
            # SALES ORDER ITEM
            # UPDATE DESCRIPTIONS
            updated_record_ids_so = []
            if frappe.db.exists("Custom Field", "Sales Order Item-id_en"):
                records_to_update_so_en = frappe.db.sql("""SELECT `name`, parent, item_language 
                        FROM `tabSales Order Item`
                        WHERE (`item_description_en` IS NULL 
                            OR `item_description_en` = ''	
                            OR `item_description_en` LIKE '%<div class="ql-editor read-mode"><p><br></p></div>%')
                """, as_dict=True)
                # The list of IDs of the updated records
                updated_record_ids_so += [f"'{record['parent']}'" for record in records_to_update_so_en]
                
                frappe.db.sql("""UPDATE `tabSales Order Item`
                                    SET `item_description_en` = 
                                        CASE
                                            -- If `item_description_en` is null, empty, or contains the specific HTML pattern
                                            WHEN `item_description_en` IS NULL 
                                                OR `item_description_en` = ''	
                                                OR `item_description_en` LIKE '%<div class="ql-editor read-mode"><p><br></p></div>%'
                                            THEN 
                                                -- If `id_en` is null, empty, or contains the specific HTML pattern
                                                CASE 
                                                    WHEN `id_en` IS NULL 
                                                        OR `id_en` = '' 
                                                        OR `id_en` LIKE '%<div class="ql-editor read-mode"><p><br></p></div>%'
                                                    THEN `description` -- If `id_en` also doesn't have valid content, use `description`
                                                    ELSE `id_en` -- Otherwise, use `id_en`
                                                END
                                            ELSE `item_description_en` -- If `item_description_en` does not match the conditions, do nothing
                                        END""")
                # frappe.delete_doc("Custom Field", "Sales Order Item-id_en", force=1)
            if frappe.db.exists("Custom Field", "Sales Order Item-id_fr"):
                records_to_update_so_fr = frappe.db.sql("""SELECT `name`, parent, item_language 
                        FROM `tabSales Order Item`
                        WHERE (`item_description_fr` IS NULL 
                            OR `item_description_fr` = ''	
                            OR `item_description_fr` LIKE '%<div class="ql-editor read-mode"><p><br></p></div>%')
                """, as_dict=True)
                # The list of IDs of the updated records
                updated_record_ids_so += [f"'{record['parent']}'" for record in records_to_update_so_fr]
                frappe.db.sql("""UPDATE `tabSales Order Item`
                                    SET `item_description_fr` = 
                                        CASE
                                            -- If `item_description_fr` is null, empty, or contains the specific HTML pattern
                                            WHEN `item_description_fr` IS NULL 
                                                OR `item_description_fr` = ''	
                                                OR `item_description_fr` LIKE '%<div class="ql-editor read-mode"><p><br></p></div>%'
                                            THEN 
                                                -- If `id_fr` is null, empty, or contains the specific HTML pattern
                                                CASE 
                                                    WHEN `id_fr` IS NULL 
                                                        OR `id_fr` = '' 
                                                        OR `id_fr` LIKE '%<div class="ql-editor read-mode"><p><br></p></div>%'
                                                    THEN `description` -- If `id_fr` also doesn't have valid content, use `description`
                                                    ELSE `id_fr` -- Otherwise, use `id_fr`
                                                END
                                            ELSE `item_description_fr` -- If `item_description_fr` does not match the conditions, do nothing
                                        END""")
                # frappe.delete_doc("Custom Field", "Sales Order Item-id_fr", force=1)
            if frappe.db.exists("Custom Field", "Sales Order Item-id_de"):
                records_to_update_so_de = frappe.db.sql("""SELECT `name`, parent, item_language 
                        FROM `tabSales Order Item`
                        WHERE (`item_description_de` IS NULL 
                            OR `item_description_de` = ''	
                            OR `item_description_de` LIKE '%<div class="ql-editor read-mode"><p><br></p></div>%')
                """, as_dict=True)
                # The list of IDs of the updated records
                updated_record_ids_so += [f"'{record['parent']}'" for record in records_to_update_so_de]
                frappe.db.sql("""UPDATE `tabSales Order Item`
                                    SET `item_description_de` = 
                                        CASE
                                            -- If `item_description_de` is null, empty, or contains the specific HTML pattern
                                            WHEN `item_description_de` IS NULL 
                                                OR `item_description_de` = ''	
                                                OR `item_description_de` LIKE '%<div class="ql-editor read-mode"><p><br></p></div>%'
                                            THEN 
                                                -- If `id_de` is null, empty, or contains the specific HTML pattern
                                                CASE 
                                                    WHEN `id_de` IS NULL 
                                                        OR `id_de` = '' 
                                                        OR `id_de` LIKE '%<div class="ql-editor read-mode"><p><br></p></div>%'
                                                    THEN `description` -- If `id_de` also doesn't have valid content, use `description`
                                                    ELSE `id_de` -- Otherwise, use `id_de`
                                                END
                                            ELSE `item_description_de` -- If `item_description_de` does not match the conditions, do nothing
                                        END""")
                # frappe.delete_doc("Custom Field", "Sales Order Item-id_de", force=1)
            
            # UPDATE ITEM NAMES
            if frappe.db.exists("Custom Field", "Sales Order Item-item_name_en"):
                records_to_update_so_item_en = frappe.db.sql("""SELECT `name`, parent, item_language 
                        FROM `tabSales Order Item`
                        WHERE `item_name_en` IS NULL 
                            OR `item_name_en` = ''
                """, as_dict=True)
                # The list of IDs of the updated records
                updated_record_ids_so += [f"'{record['parent']}'" for record in records_to_update_so_item_en]
                frappe.db.sql("update `tabSales Order Item` set `item_name_en` = `item_name` where item_name_en is null;")
                
            if frappe.db.exists("Custom Field", "Sales Order Item-item_name_de"):
                records_to_update_so_item_de = frappe.db.sql("""SELECT `name`, parent, item_language 
                        FROM `tabSales Order Item`
                        WHERE `item_name_de` IS NULL 
                            OR `item_name_de` = ''
                """, as_dict=True)
                # The list of IDs of the updated records
                updated_record_ids_so += [f"'{record['parent']}'" for record in records_to_update_so_item_de]
                frappe.db.sql("update `tabSales Order Item` set `item_name_de` = `item_name` where item_name_de is null;")

            if frappe.db.exists("Custom Field", "Sales Order Item-item_name_fr"):
                records_to_update_so_item_fr = frappe.db.sql("""SELECT `name`, parent, item_language 
                        FROM `tabSales Order Item`
                        WHERE `item_name_fr` IS NULL 
                            OR `item_name_fr` = ''
                """, as_dict=True)
                # The list of IDs of the updated records
                updated_record_ids_so += [f"'{record['parent']}'" for record in records_to_update_so_item_fr]
                frappe.db.sql("update `tabSales Order Item` set `item_name_fr` = `item_name` where item_name_fr is null;")



            # QUOTATION ITEM
            # UPDATE DESCRIPTIONS
            updated_record_ids_quo = []
            if frappe.db.exists("Custom Field", "Quotation Item-id_en"):
                records_to_update_quo_en = frappe.db.sql("""SELECT `name`, parent, item_language 
                        FROM `tabQuotation Item`
                        WHERE (`item_description_en` IS NULL 
                            OR `item_description_en` = ''	
                            OR `item_description_en` LIKE '%<div class="ql-editor read-mode"><p><br></p></div>%')
                """, as_dict=True)
                # The list of IDs of the updated records
                updated_record_ids_quo += [f"'{record['parent']}'" for record in records_to_update_quo_en]
                frappe.db.sql("""UPDATE `tabQuotation Item`
                                    SET `item_description_en` = 
                                        CASE
                                            -- If `item_description_en` is null, empty, or contains the specific HTML pattern
                                            WHEN `item_description_en` IS NULL 
                                                OR `item_description_en` = ''	
                                                OR `item_description_en` LIKE '%<div class="ql-editor read-mode"><p><br></p></div>%'
                                            THEN 
                                                -- If `id_en` is null, empty, or contains the specific HTML pattern
                                                CASE 
                                                    WHEN `id_en` IS NULL 
                                                        OR `id_en` = '' 
                                                        OR `id_en` LIKE '%<div class="ql-editor read-mode"><p><br></p></div>%'
                                                    THEN `description` -- If `id_en` also doesn't have valid content, use `description`
                                                    ELSE `id_en` -- Otherwise, use `id_en`
                                                END
                                            ELSE `item_description_en` -- If `item_description_en` does not match the conditions, do nothing
                                        END""")
                # frappe.delete_doc("Custom Field", "Sales Order Item-id_en", force=1)
            if frappe.db.exists("Custom Field", "Quotation Item-id_fr"):
                records_to_update_quo_fr = frappe.db.sql("""SELECT `name`, parent, item_language 
                        FROM `tabQuotation Item`
                        WHERE (`item_description_fr` IS NULL 
                            OR `item_description_fr` = ''	
                            OR `item_description_fr` LIKE '%<div class="ql-editor read-mode"><p><br></p></div>%')
                """, as_dict=True)
                # The list of IDs of the updated records
                updated_record_ids_quo += [f"'{record['parent']}'" for record in records_to_update_quo_fr]
                frappe.db.sql("""UPDATE `tabQuotation Item`
                                    SET `item_description_fr` = 
                                        CASE
                                            -- If `item_description_fr` is null, empty, or contains the specific HTML pattern
                                            WHEN `item_description_fr` IS NULL 
                                                OR `item_description_fr` = ''	
                                                OR `item_description_fr` LIKE '%<div class="ql-editor read-mode"><p><br></p></div>%'
                                            THEN 
                                                -- If `id_fr` is null, empty, or contains the specific HTML pattern
                                                CASE 
                                                    WHEN `id_fr` IS NULL 
                                                        OR `id_fr` = '' 
                                                        OR `id_fr` LIKE '%<div class="ql-editor read-mode"><p><br></p></div>%'
                                                    THEN `description` -- If `id_fr` also doesn't have valid content, use `description`
                                                    ELSE `id_fr` -- Otherwise, use `id_fr`
                                                END
                                            ELSE `item_description_fr` -- If `item_description_fr` does not match the conditions, do nothing
                                        END""")
                # frappe.delete_doc("Custom Field", "Sales Order Item-id_fr", force=1)
            if frappe.db.exists("Custom Field", "Quotation Item-id_de"):
                records_to_update_quo_de = frappe.db.sql("""SELECT `name`, parent, item_language 
                        FROM `tabQuotation Item`
                        WHERE (`item_description_de` IS NULL 
                            OR `item_description_de` = ''	
                            OR `item_description_de` LIKE '%<div class="ql-editor read-mode"><p><br></p></div>%')
                """, as_dict=True)
                # The list of IDs of the updated records
                updated_record_ids_quo += [f"'{record['parent']}'" for record in records_to_update_quo_de]
                
                frappe.db.sql("""UPDATE `tabQuotation Item`
                                    SET `item_description_de` = 
                                        CASE
                                            -- If `item_description_de` is null, empty, or contains the specific HTML pattern
                                            WHEN `item_description_de` IS NULL 
                                                OR `item_description_de` = ''	
                                                OR `item_description_de` LIKE '%<div class="ql-editor read-mode"><p><br></p></div>%'
                                            THEN 
                                                -- If `id_de` is null, empty, or contains the specific HTML pattern
                                                CASE 
                                                    WHEN `id_de` IS NULL 
                                                        OR `id_de` = '' 
                                                        OR `id_de` LIKE '%<div class="ql-editor read-mode"><p><br></p></div>%'
                                                    THEN `description` -- If `id_de` also doesn't have valid content, use `description`
                                                    ELSE `id_de` -- Otherwise, use `id_de`
                                                END
                                            ELSE `item_description_de` -- If `item_description_de` does not match the conditions, do nothing
                                        END""")
                # frappe.delete_doc("Custom Field", "Quotation Item-id_fr", force=1)
            
            # UPDATE ITEM NAMES
            if frappe.db.exists("Custom Field", "Quotation Item-item_name_en"):
                records_to_update_quo_item_en = frappe.db.sql("""SELECT `name`, parent, item_language 
                        FROM `tabQuotation Item`
                        WHERE `item_name_en` IS NULL 
                            OR `item_name_en` = ''
                """, as_dict=True)
                # The list of IDs of the updated records
                updated_record_ids_quo += [f"'{record['parent']}'" for record in records_to_update_quo_item_en]
                frappe.db.sql("""update `tabQuotation Item` set `item_name_en` = `item_name` where `item_name_en` IS NULL 
                            OR `item_name_en` = '' """)
                
            if frappe.db.exists("Custom Field", "Quotation Item-item_name_de"):
                records_to_update_quo_item_de = frappe.db.sql("""SELECT `name`, parent, item_language 
                        FROM `tabQuotation Item`
                        WHERE `item_name_de` IS NULL 
                            OR `item_name_de` = ''
                """, as_dict=True)
                # The list of IDs of the updated records
                updated_record_ids_quo += [f"'{record['parent']}'" for record in records_to_update_quo_item_de]
                frappe.db.sql("""update `tabQuotation Item` set `item_name_de` = `item_name` where `item_name_de` IS NULL 
                            OR `item_name_de` = ''""")

            if frappe.db.exists("Custom Field", "Quotation Item-item_name_fr"):
                records_to_update_quo_item_fr = frappe.db.sql("""SELECT `name`, parent, item_language 
                        FROM `tabQuotation Item`
                        WHERE `item_name_fr` IS NULL 
                            OR `item_name_fr` = ''
                """, as_dict=True)
                # The list of IDs of the updated records
                updated_record_ids_quo += [f"'{record['parent']}'" for record in records_to_update_quo_item_fr]
                frappe.db.sql("""update `tabQuotation Item` set `item_name_fr` = `item_name` where `item_name_fr` IS NULL 
                            OR `item_name_fr` = ''""")

            # PURCHASE ORDER ITEM
            # UPDATE DESCRIPTIONS
            updated_record_ids_po = []
            if frappe.db.exists("Custom Field", "Purchase Order Item-item_description_en"):
                records_to_update_po_en = frappe.db.sql("""SELECT `name`, parent
                        FROM `tabPurchase Order Item`
                        WHERE (`item_description_en` IS NULL 
                            OR `item_description_en` = ''	
                            OR `item_description_en` LIKE '%<div class="ql-editor read-mode"><p><br></p></div>%')
                """, as_dict=True)
                # The list of IDs of the updated records
                updated_record_ids_po += [f"'{record['parent']}'" for record in records_to_update_po_en]
                frappe.db.sql("""update `tabPurchase Order Item` set `item_description_en` = `description` 
                              where 
                              `item_description_en` IS NULL 
                                OR `item_description_en` = ''
                                OR `item_description_en` LIKE '%<div class="ql-editor read-mode"><p><br></p></div>%';""")
                
            if frappe.db.exists("Custom Field", "Purchase Order Item-item_description_de"):
                records_to_update_po_de = frappe.db.sql("""SELECT `name`, parent
                        FROM `tabPurchase Order Item`
                        WHERE (`item_description_de` IS NULL 
                            OR `item_description_de` = ''	
                            OR `item_description_de` LIKE '%<div class="ql-editor read-mode"><p><br></p></div>%')
                """, as_dict=True)
                # The list of IDs of the updated records
                updated_record_ids_po += [f"'{record['parent']}'" for record in records_to_update_po_de]
                frappe.db.sql("""update `tabPurchase Order Item` set `item_description_de` = `description` where `item_description_de` IS NULL 
                                                OR `item_description_de` = ''	
                                                OR `item_description_de` LIKE '%<div class="ql-editor read-mode"><p><br></p></div>%';""")

            if frappe.db.exists("Custom Field", "Purchase Order Item-item_description_fr"):
                records_to_update_po_fr = frappe.db.sql("""SELECT `name`, parent
                        FROM `tabPurchase Order Item`
                        WHERE (`item_description_fr` IS NULL 
                            OR `item_description_fr` = ''	
                            OR `item_description_fr` LIKE '%<div class="ql-editor read-mode"><p><br></p></div>%')
                """, as_dict=True)
                # The list of IDs of the updated records
                updated_record_ids_po += [f"'{record['parent']}'" for record in records_to_update_po_fr]
                frappe.db.sql("""update `tabPurchase Order Item` set `item_description_fr` = `description` where `item_description_fr` IS NULL 
                                                OR `item_description_fr` = ''	
                                                OR `item_description_fr` LIKE '%<div class="ql-editor read-mode"><p><br></p></div>%';""")
                
            # UPDATE ITEM NAMES
            if frappe.db.exists("Custom Field", "Purchase Order Item-item_name_en"):
                records_to_update_po_item_en = frappe.db.sql("""SELECT `name`, parent
                        FROM `tabPurchase Order Item`
                        WHERE `item_name_en` IS NULL 
                            OR `item_name_en` = ''
                """, as_dict=True)
                # The list of IDs of the updated records
                updated_record_ids_po += [f"'{record['parent']}'" for record in records_to_update_po_item_en]
                frappe.db.sql("""update `tabPurchase Order Item` set `item_name_en` = `item_name` where `item_name_en` IS NULL 
                            OR `item_name_en` = ''""")
                
            if frappe.db.exists("Custom Field", "Purchase Order Item-item_name_de"):
                records_to_update_po_item_de = frappe.db.sql("""SELECT `name`, parent
                        FROM `tabPurchase Order Item`
                        WHERE `item_name_de` IS NULL 
                            OR `item_name_de` = ''
                """, as_dict=True)
                # The list of IDs of the updated records
                updated_record_ids_po += [f"'{record['parent']}'" for record in records_to_update_po_item_de]
                frappe.db.sql("""update `tabPurchase Order Item` set `item_name_de` = `item_name` where `item_name_de` IS NULL 
                            OR `item_name_de` = ''""")
                
            if frappe.db.exists("Custom Field", "Purchase Order Item-item_name_fr"):
                records_to_update_po_item_fr = frappe.db.sql("""SELECT `name`, parent
                        FROM `tabPurchase Order Item`
                        WHERE `item_name_fr` IS NULL 
                            OR `item_name_fr` = ''
                """, as_dict=True)
                # The list of IDs of the updated records
                updated_record_ids_po += [f"'{record['parent']}'" for record in records_to_update_po_item_fr]
                frappe.db.sql("""update `tabPurchase Order Item` set `item_name_fr` = `item_name` where `item_name_fr` IS NULL 
                            OR `item_name_fr` = ''""")
                
                
            # # Join the list into a comma-separated string
            updated_record_ids_sm = ", ".join(updated_record_ids_sm)
            updated_record_ids_so = ", ".join(updated_record_ids_so)
            updated_record_ids_quo = ", ".join(updated_record_ids_quo)
            updated_record_ids_po = ", ".join(updated_record_ids_po)
            
            modified_by = frappe.session.user
            update_timestamp = int(self.update_timestamp)
            
            if update_timestamp:
                if updated_record_ids_sm:
                    frappe.db.sql("""update `tabSoftware Maintenance` set `modified` = '{modified}', `modified_by` = '{modified_by}' where name in ({updated_sm_ids})""".format(modified= now(), modified_by= modified_by, updated_sm_ids=updated_record_ids_sm))
                if updated_record_ids_so:
                    frappe.db.sql("""update `tabSales Order` set `modified` = '{modified}', `modified_by` = '{modified_by}' where name in ({updated_so_ids}) """.format(modified= now(), modified_by= modified_by, updated_so_ids=updated_record_ids_so))
                if updated_record_ids_quo:
                    frappe.db.sql("""update `tabQuotation` set `modified` = '{modified}', `modified_by` = '{modified_by}' where name in ({updated_quo_ids})""".format(modified= now(), modified_by= modified_by, updated_quo_ids=updated_record_ids_quo))
                if updated_record_ids_po:
                    frappe.db.sql("""update `tabPurchase Order` set `modified` = '{modified}', `modified_by` = '{modified_by}' where name in ({updated_po_ids}) """.format(modified= now(), modified_by= modified_by, updated_quo_ids=updated_record_ids_po))
            frappe.db.commit()
            return {"message":"""<h3>The script has run and had updated all Item Name and Item Descriptions in Software Maintenance, Sales Order, Quotation and Purchase Order:</h3>
                    <ul>
                        <li>Copied the old item description data from id_xx field to item_description_xx</li>
                        <li>Copied the old item_name data from item_name field to item_name_xx</li>
                    </ul>
                    <p>For further information check in SimpaTec Settings page and consult your project manager.</p> """, "title": "Success"}   
        except Exception as ex:
            frappe.db.rollback()
            frappe.log_error(ex)
            return {"message":"There was some error occured in the process, Please check error logs.", "title":"Error" }

    @frappe.whitelist()
    def update_software_maintenance_items(self):
        try:
            frappe.publish_progress(0, title='Updating Software Maintenances', description='Starting update...')
            # Remove Wrong field of reccuring_maintenance_amount and reoccuring_maintenance_amount if exist
            if frappe.db.exists("Custom Field", "Sales Order Item-reoccuring_maintenance_amount"):
                frappe.delete_doc("Custom Field", "Sales Order Item-reoccuring_maintenance_amount", force=1)
            if frappe.db.exists("Custom Field", "Sales Order Item-reccuring_maintenance_amount"):
                # First set the value of wrong `reoccurring_maintenance_amount` field into `reoccurring_maintenance_amount`
                frappe.db.sql("update `tabSales Order Item` set `reoccurring_maintenance_amount` = `reccuring_maintenance_amount` where item_type = 'Maintenance Item'")
                # Now removing the field
                frappe.delete_doc("Custom Field", "Sales Order Item-reccuring_maintenance_amount", force=1)
            if frappe.db.exists("Custom Field", "Sales Order Item-einkaufspreis"):
                # first update the field value into new one
                frappe.db.sql("update `tabSales Order Item` set `purchase_price` = `einkaufspreis` ")
                # now remove the field and its section
                frappe.delete_doc("Custom Field", "Sales Order Item-einkauf", force=1) # section
                frappe.delete_doc("Custom Field", "Sales Order Item-einkaufspreis", force=1) # field
            
            update_timestamp = int(self.update_timestamp)
            """Query for removing all previous Software maintenance Items"""
            frappe.db.sql("DELETE FROM `tabSoftware Maintenance Item`")
            software_maintenances = frappe.get_all("Software Maintenance", fields=["sales_order", "name"], filters=[["sales_order","is","set"]])
            total_rows = len(software_maintenances)
            for index, s_m in enumerate(software_maintenances):
                so_items = frappe.get_all("Sales Order Item", filters={"parent": s_m.sales_order}, fields=["*"])
                if len(so_items) > 0:
                    for item in so_items:   
                        software_maintenance_items = frappe.new_doc("Software Maintenance Item")

                        if item.start_date is not None:
                            item.start_date = item.start_date + timedelta(days=365)
                        if item.end_date is not None:
                            item.end_date = item.end_date + timedelta(days=365)
                            if item.start_date is not None and item.end_date is not None:
                                days_diff = item.end_date - item.start_date
                                if days_diff == 365:
                                    item.end_date = item.end_date - timedelta(days=1)
                        if item.item_type == "Maintenance Item":
                            item.rate = item.reoccurring_maintenance_amount
                            item.reoccurring_maintenance_amount = item.reoccurring_maintenance_amount
                        else:
                            item.rate = 0
                            item.reoccurring_maintenance_amount = 0

                        software_maintenance_items.update({
                            "idx": item.idx,
                            "item_code": item.item_code,
                            "item_name": item.item_name,
                            "description": item.description,
                            "conversion_factor": item.conversion_factor,
                            "qty": item.qty,
                            "rate": item.reoccurring_maintenance_amount,
                            "reoccurring_maintenance_amount": item.reoccurring_maintenance_amount,
                            "uom": item.uom,
                            "item_language": item.item_language,
                            "delivery_date": frappe.db.get_value("Sales Order", s_m.sales_order, "transaction_date"),
                            "start_date": item.start_date,
                            "end_date": item.end_date,
                            "purchase_price": item.purchase_price,
                            'parent': s_m.name,
                            'parentfield': 'items',
                            'parenttype': "Software Maintenance"
                        })
                        software_maintenance_items.insert(ignore_permissions=True)
                    modified_by = frappe.session.user
                    # frappe.db.set_value("Software Maintenance", s_m.name, "assign_to", frappe.db.get_value("Sales Order", s_m.sales_order, "assigned_to"), update_modified=False)
                    frappe.db.set_value("Sales Order", s_m.sales_order, "sales_order_type", "First Sale", update_modified=update_timestamp)
                    frappe.db.set_value("Sales Order", s_m.sales_order, "software_maintenance", s_m.name, update_modified=update_timestamp)
                    if update_timestamp:
                        frappe.db.sql("""update `tabSoftware Maintenance` set `modified` = '{modified}', `modified_by` = '{modified_by}' where `name` = '{sm_name}'""".format(modified= now(), modified_by= modified_by, sm_name=s_m.name))
                        frappe.db.sql("""update `tabSales Order` set `sales_order_type` = 'Reoccuring Maintenance', `modified` = '{modified}', `modified_by` = '{modified_by}' where `sales_order_type` = 'Follow Up Maintenance' """.format(modified= now(), modified_by= modified_by))
                    else:
                        frappe.db.sql("""update `tabSales Order` set `sales_order_type` = 'Reoccuring Maintenance' where `sales_order_type` = 'Follow Up Maintenance' """)
                    frappe.db.commit()
                index += 1
                progress = int( (index / total_rows) * 100)
                frappe.publish_progress(progress, title='Updating Software Maintenances', description=f'Processing row {index}/{total_rows}')
            return {"message":"""<h3>The script has run and had updated all Software Maintenance:</h3>
                    <ul>
                        <li>existing items table have been cleared from all Software Maintenance</li>
                        <li>the linked Sales Invoice in Software Maintenance has been updated to "First Sale"</li>
                        <li>the items from that Sales Invoice have been fetched into the Software Maintenance item table</li>
                        <li>all Sales Orders with sales_order_type "Follow-Up Maintenance have been updated to "Reoccurring Maintenance"</li>
                    </ul>
                    <p>The script has ignored missing date like start/end dates, rates, etc.</p>
                    <p>For further information check in SimpaTec Settings page and consult your project manager.</p> """, "title": "Success"}   
        except Exception as ex:
            frappe.db.rollback()
            frappe.log_error(ex)
            return {"message":"There was some error occured in the process, Please check error logs.", "title":"Error" }