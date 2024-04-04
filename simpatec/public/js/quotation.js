frappe.ui.form.on('Quotation', {
	refresh: function(frm) {

        function addClearIconToField(field) {
            if (!field.$clear_icon_appended) {
                field.$clear_icon_appended = true;

				var $clearIcon = $('<span id="xsimpactggleicon" class="clear-icon" style="cursor: pointer; position: absolute; right: 35px; top: 50%; transform: translateY(-50%); font-size: 15px; width: 18px; height: 18px; line-height: 18px; text-align: center; border-radius: 50%;  color: #1C2126;"><svg class="icon "> <use href="#icon-filter-x"></use> </svg> </span>');
                field.$input.parent().css('position', 'relative'); 
                field.$input.css('position', 'relative'); 
                field.$input.after($clearIcon);

                $clearIcon.on('click', function() {
					let qd = cur_frm.fields_dict["anschreiben_vorlage"].get_query();
					var x = document.getElementById("xsimpactggleicon").children[0];
					if (!(qd == undefined) && qd.filters.language === frm.doc.language){
						x.innerHTML = '<use href="#icon-filter"></use>';
						frm.set_query("anschreiben_vorlage", () => {
							let filters = {};
							/* return {
								filters: filters
							} */
						});
					}
					else{
						x.innerHTML = '<use href="#icon-filter-x"></use>';
						frm.set_query("anschreiben_vorlage", () => {
							let filters = {};
							if (frm.doc.language) filters["language"] = frm.doc.language;
							return {
								filters: filters
							}
						});

					}
                    					
					frm.set_value(field.df.fieldname, '');
                });
            }
        }


        $.each(frm.fields_dict, function(fieldname, field) {
            
			if (fieldname == 'anschreiben_vorlage') {
                addClearIconToField(field);
            }
        });
    },
	setup: function(frm){
		frm.set_query("anschreiben_vorlage", () => {
			let filters = {};
			if (frm.doc.language) filters["language"] = frm.doc.language;
			return {
				filters: filters
			}
		});
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

frappe.ui.form.on('Quotation Item',{
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
	
});