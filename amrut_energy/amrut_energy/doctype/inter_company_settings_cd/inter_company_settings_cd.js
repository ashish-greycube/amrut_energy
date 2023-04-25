// Copyright (c) 2023, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Inter Company Settings CD', {

	setup: function(frm) {
		frm.set_query('sending_bank_account', 'company_bank_mappings', (frm, cdt, cdn) => {
			var d = frappe.model.get_doc(cdt, cdn);
				return {
					filters: {
						account_type: 'Bank',
						company:d.sending_company
					}
				}				
		})
		frm.set_query('receiving_bank_account', 'company_bank_mappings', (frm, cdt, cdn) => {
			var d = frappe.model.get_doc(cdt, cdn);
			return {
				filters: {
					account_type: 'Bank',
					company:d.receiving_company
				}
			}
		})

	}
});
