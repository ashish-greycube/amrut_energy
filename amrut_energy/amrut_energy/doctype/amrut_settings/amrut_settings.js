// Copyright (c) 2020, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Amrut Settings', {
	setup: function(frm) {
		frm.set_query('pdf_print_format_for_url', () => {
			return {
				filters: {
					doc_type: 'Quotation'
				}
			}
		})
	}
});
