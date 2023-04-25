frappe.ui.form.on('Payment Entry', {
    refresh: function (frm) {
        if (frm.doc.docstatus == 1 && frm.doc.create_inter_company_journal_entry_cf == 1) {
            frm.add_custom_button(__("Inter Company JE"), function () {
                frappe.route_options = {
                    "user_remark": frm.doc.name
                };
                frappe.set_route("List", "Journal Entry");
            });
        }
    }
})