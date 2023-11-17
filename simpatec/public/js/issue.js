
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

							let color;
							if (d.status === 'Active'){
								color = "green";
							}
							else {
								color = "red";
							}

							frm.dashboard.set_headline_alert(`
								<div class="row">
									<div class="col-xs-12">
										<span class="indicator whitespace-nowrap ${color}">
											<span class="hidden-xs">
												<a style="text-decoration: underline;" onclick="frappe.set_route('Form', 'Software Maintenance', '${d.name}');">The Software Maintenance ${d.name} is <b>${d.status}</b>. Expiry on: <b>${d.performance_period_end}</b>. Click to open</a>
											</span>
										</span>
									</div>
								</div>
							`);
                        });
                    }
                });
            }
		}
	}
})