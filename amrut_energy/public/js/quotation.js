frappe.ui.form.on('Quotation', {
	setup: function(frm) {
        frappe.db.get_single_value('Amrut Settings', 'product_bundle_item_group')
            .then(product_bundle_item_group => {
                frm.set_query('product_bundle_item_cf', () => {
                    return {
                        filters: {
                            item_group: product_bundle_item_group
                        }
                    }
                })                
            });
    },
    refresh: function(frm) {
        frm.toggle_display(['create_product_bundle_cf'], frm.is_new() === undefined);
    },
    validate: function(frm) {
        frm.set_df_property('create_product_bundle_cf', 'hidden', 0)
    },
    create_product_bundle_process: function(frm) {
        if(frm.fields_dict.items.grid.get_selected().length===0) {
            frappe.throw(__('Plese select item to proceed.'))
        }
        frappe.call({
            method: 'amrut_energy.api.create_product_bundle',
            args: {
                doc: frm.doc,
                qo_items:frm.fields_dict.items.grid.get_selected()
            },
            btn: $('.primary-action'),
            freeze: true,
            callback: (r) => {
                console.log('r1',r)
                cur_frm.reload_doc()
            },
            error: (r) => {
                console.log('r2',r)
                frappe.show_alert("Something went wrong please try again");
            }
        })
    },
    create_product_bundle_cf: function(frm) {
        if (!frm.doc.product_bundle_item_cf) {
            frappe.throw(__('Plese select value for Product Bundle Item to proceed.'))
        }        
        else if (frm.is_dirty()==1) {
            frm.save().then(()=> frappe.show_alert("Quotation is saved now. Do the item selection and press 'Create Product Bundle' button."));
        }
        else{
            frm.trigger('create_product_bundle_process');  
        }

    }
})

frappe.ui.form.on('Quotation Item', {
	rate: function (frm,cdt,cdn) {
		// check entered price is not less than sales price
        let row = locals[cdt][cdn];
		if (row.price_list_rate && row.rate < row.price_list_rate ) {
			frappe.throw(__('Rate entered by you is <b> {0} </b>. <br> It cannot be less than sales rate of <b> {1} </b>.',[row.rate, row.price_list_rate]))
		}
	}
})