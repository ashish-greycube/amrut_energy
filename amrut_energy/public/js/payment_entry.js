frappe.ui.form.on('Payment Entry', {
    refresh: function (frm) {
        if (frm.doc.docstatus == 1 && frm.doc.create_inter_company_journal_entry_cf == 1) {
            frm.add_custom_button(__("View Inter JE"), function () {
                frappe.route_options = {
                    "user_remark": frm.doc.name
                };
                frappe.set_route("List", "Journal Entry");
            });
        }
        if (frm.doc.docstatus == 1 && frm.doc.create_inter_company_journal_entry_cf == 0 && frm.doc.receiving_company_cf) {
            frm.add_custom_button(__("Create Inter JE"), function () {
                frappe.call({
                    method: 'amrut_energy.doc_events.on_submit_payment_entry_create_inter_company_je',
                    args: {
                        docname: frm.doc.name,
                        receiving_company_cf:frm.doc.receiving_company_cf
                    },
                    // disable the button until the request is completed
                    btn: $('.primary-action'),
                    // freeze the screen until the request is completed
                    freeze: true,
                    callback: (r) => {
                        frm.reload_doc();
                        // on success
                    },
                    error: (r) => {
                        // on error
                    }
                })
            });
        }        
    }
})