frappe.ui.form.on('Purchase Order', {
	refresh: function(frm){
		let btn = cur_frm.fields_dict.items.grid.add_custom_button("Remove Item Description", function(){ 
			if (!is_null(frm.fields_dict.items.grid.get_selected_children())) {
				$.each(frm.fields_dict.items.grid.get_selected_children(), (k, v) => {
					v.description = ""
					if (v.item_language == 'en'){
						v.item_description_en = ""
					} else if(v.item_language == 'de'){
						v.item_description_de = ""
					} else if (v.item_language == 'fr') {
						v.item_description_fr = ""
					}
					v.__checked = 0
				})
			}else{
				$.each(frm.doc.items, (k, v) => {
					v.description = ""
					if (v.item_language == 'en') {
						v.item_description_en = ""
					} else if (v.item_language == 'de') {
						v.item_description_de = ""
					} else if (v.item_language == 'fr') {
						v.item_description_fr = ""
					}
					v.__checked = 0
				})
			}
			refresh_field("items");
			frm.dirty()
			frappe.msgprint("Item Description Removed")
		})
		btn.addClass("btn-secondary")
		btn.removeClass("btn-default")
	},
	setup: function(frm){
		frm.copy_from_previous_row = function(parentfield, current_row, fieldnames){
			

			var data = frm.doc[parentfield];
			let idx = data.indexOf(current_row);
			if (data.length === 1 || data[0] === current_row) return;
			
			if (typeof fieldnames === "string") {
				fieldnames = [fieldnames];
			}			
			
			$.each(fieldnames, function (i, fieldname) {
				frappe.model.set_value(
					current_row.doctype,
					current_row.name,
					fieldname,
					data[idx - 1][fieldname]
				);
			});
		},
		frm.auto_fill_all_empty_rows = function(doc, dt, dn, table_fieldname, fieldname) {
			var d = locals[dt][dn];
			if(d[fieldname]){
				var cl = doc[table_fieldname] || [];
				for(var i = 0; i < cl.length; i++) {
					if(cl[i][fieldname]) cl[i][fieldname] = d[fieldname];
				}
			}
			refresh_field(table_fieldname);
		},
		frm.occurence_len = function(arr, element){
			
			return arr.filter(
				(ele) => ele.item_language == element
			).length;
		}
	}
});

frappe.ui.form.on('Purchase Order Item',{
	//
	item_name: function(frm, cdt, cdn){

		var data = frm.doc.items;
		var row = locals[cdt][cdn];
		if (data.length === 1 || data[0] === row) {
			if (frm.doc.language){
				row.item_language = frm.doc.language;
				refresh_field("item_language", cdn, "items");
			}
			
		} else {
			frm.copy_from_previous_row("items", row, ["item_language"]);
		}	
	},

	item_language: function(frm, cdt, cdn){
		
		var data = frm.doc.items;
		
		var row = locals[cdt][cdn];
		if(!(frm.doc.language=== row.item_language)){			
			let row_occurence = frm.occurence_len(data, row.item_language);
			if (row_occurence < data.length && !cur_dialog){
			
				frappe.confirm("💬"+__("  The language <b>{0}</b> in the just edited row is different to the others. Should <b>{0}</b> apply to all rows?", [ row.item_language]),
				()=>{
					frm.auto_fill_all_empty_rows(frm.doc, cdt, cdn, "items", "item_language");
				}, ()=>{
					//cancel
				})
			}
			//
		}
		else if (frm.doc.language=== row.item_language){
			
			let row_occurence = frm.occurence_len(data, row.item_language);
			if (row_occurence < data.length && !cur_dialog){
				//				
				frappe.confirm("💬"+__("    The language <b>'{0}'</b> in the just edited row is different to the others. Should <b>'{0}'</b> apply to all rows?", [ row.item_language]),
					()=>{
							frm.auto_fill_all_empty_rows(frm.doc, cdt, cdn, "items", "item_language");
						}, 
					()=>{
						//cancel
					}
				)
			}
		}	
	},

	schedule_date: function(frm, cdt, cdn){
		let cur_row = locals[cdt][cdn]
		frm.auto_fill_all_empty_rows(frm.doc, cdt, cdn, "items", "schedule_date");
		frm.set_value("schedule_date", cur_row.schedule_date)
	}
	
});