frappe.ui.form.on('Stock Entry', {
    bom_no: function (frm) {
        if (frm.doc.purpose == 'Manufacture' && frm.doc.bom_no) {
            console.log(frm.doc.bom_no, '2')
            frappe.db.get_value('BOM', frm.doc.bom_no, 'quantity')
                .then(r => {
                    let bom_qty = r.message.quantity
                    let se_qty = frm.doc.fg_completed_qty
                    frappe.db.get_list('BOM Additional Cost CT', {
                        fields: ['expense_account', 'description', 'amount'],
                        filters: {
                            parent: frm.doc.bom_no
                        }
                    }).then(additional_costs => {
                        if (additional_costs) {
                            additional_costs.forEach(bom_cost => {
                                let row = frm.add_child('additional_costs', {
                                    expense_account: bom_cost.expense_account,
                                    description: bom_cost.description,
                                    exchange_rate: 1,
                                    amount: (se_qty / bom_qty) * bom_cost.amount,
                                    base_amount: (se_qty / bom_qty) * bom_cost.amount,

                                });

                            });
                            frm.refresh_field('additional_costs');
                            frappe.show_alert('Additonal Cost is fetched from BOM', 7);
                        }
                    })
                })
        }
    }
})