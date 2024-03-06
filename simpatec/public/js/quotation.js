frappe.ui.form.on('Quotation', {
	// refresh: function(frm) {

	// }
});

frappe.ui.form.on('Quotation Item',{
	//
	item_name: function(frm, cdt, cdn){

		var tchild = locals[cdt][cdn];
		var lng_of_arry = frm.doc.items;

		if (lng_of_arry.length > 1){
			if (tchild.idx > 1){
				var prv_val = frm.doc.items[tchild.idx-2].item_language;
				
				frappe.model.set_value(cdt,cdn, "item_language", prv_val);
				frm.refresh_field('item_language');
				console.log(prv_val);
			}
		}
		else{
			frappe.model.set_value(cdt,cdn, "item_language", frm.doc.language);
			frm.refresh_field('item_language');
		}	
	},

	item_language: function(frm, cdt, cdn){
		/* 
		onblur: {
			var child = locals[cdt][cdn];
			console.log("blob blur"+ child.idx);
            let dialog = new frappe.ui.Dialog({
			title: __("Process"),
			
		    });
		    dialog.show();
		}*/
	},
	
});