frappe.ui.form.on(cur_frm.doctype+' Item', {

	rate: function (cur_frm,cdt,cdn) {
		// check entered price is not less than sales price
        let row = locals[cdt][cdn];
		if (row.price_list_rate && row.rate < row.price_list_rate ) {
			frappe.throw(__('Rate entered by you is <b> {0} </b>. <br> It cannot be less than sales rate of <b> {1} </b>.',[row.rate, row.price_list_rate]))
		}
	}
})
