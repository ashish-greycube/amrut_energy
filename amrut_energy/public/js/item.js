frappe.ui.form.on("Item", {
    item_group: function (frm) {
        frappe.db.get_single_value('Amrut Settings', 'product_bundle_item_group')
            .then(product_bundle_item_group => {
                if (frm.doc.item_group === product_bundle_item_group) {
                    frm.set_value('is_sales_item', 1)
                    frm.set_value('is_stock_item', 1)
                }
            })
    }
});