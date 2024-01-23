frappe.listview_settings['Contact Set'] = {
    onload: function(list_view) {
        list_view.page.add_inner_button(__("Go to Contact Register"), function() {
            frappe.set_route("query-report", "Contact Register");
        })
    }
}