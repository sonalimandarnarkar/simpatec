
frappe.ui.form.on('Issue', {
	refresh: (frm) => {
		if(!frm.is_new()) {
			frm.trigger('make_dashboard');
		}
	},
	make_dashboard: (frm) => {
		if(!frm.is_new()) {
            if (frm.doc.customer && frm.doc.item_group) {
                frappe.call({
                    method: 'simpatec.api.software_maintenance',
                    args: {item_group: frm.doc.item_group, customer: frm.doc.customer},
                    callback: (r) => {
                        if(!r.message) {
                            return;
                        }
                        (r.message || []).forEach(function(d) {
                            let software_maintenance_link = `<a onclick="frappe.set_route('Form', 'Software Maintenance', '${d.name}');">Click here to go Software Maintenance ${d.name}</a>`
							frm.dashboard.set_headline_alert(
								'<div class="row">' +
									'<div class="col-xs-12">' +
										'<span class="indicator whitespace-nowrap green">' +
                                        '<span class="hidden-xs">'+ software_maintenance_link + '</span></span> ' +
									'</div>' +
								'</div>'
							);
                        });
                    }
                });
            }
		}
	}
})