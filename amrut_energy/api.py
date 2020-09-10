from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cstr

@frappe.whitelist()
def create_product_bundle(doc,qo_items):
    doc=frappe._dict(frappe.parse_json(doc))
    selected_qo_items=frappe.parse_json(qo_items)
    quotation= frappe.get_doc('Quotation', doc.name)
    qo_items=quotation.get("items")

    # check if selected is a product bundle item 
    for item in qo_items:
        for selected_qo in selected_qo_items:
            if item.name==selected_qo:
                if frappe.db.exists('Product Bundle', item.item_code) != None:
                    frappe.throw(_("Selected Item {0} is a product bundle item.".format(item.item_code)))
   
    # generate new_product_bundle_name
    new_product_bundle_name=quotation.product_bundle_item_cf+" || "+quotation.name
    if frappe.db.exists('Item', new_product_bundle_name) != None:
        i = 2
        new_product_bundle_name=quotation.product_bundle_item_cf+" || "+quotation.name+" - "+cstr(i)
        while frappe.db.exists('Item', new_product_bundle_name) != None:
            i += 1    
            new_product_bundle_name=quotation.product_bundle_item_cf+" || "+quotation.name+" - "+cstr(i)
    
    # create parent item
    product_bundle_item=frappe.get_doc('Item', quotation.product_bundle_item_cf)
    dynamic_product_bundle_group=frappe.db.get_single_value('Amrut Settings', 'dynamic_product_bundle')
    new_product_bundle_item = frappe.copy_doc(product_bundle_item)
    new_product_bundle_item.update({
        "item_code":new_product_bundle_name,
        "item_name":new_product_bundle_name,
        "item_group":dynamic_product_bundle_group,
        "is_sales_item":1,
        "is_stock_item":0,
        "auto_created":1
    })
    new_product_bundle_item.save(ignore_permissions = True)
    
    # from item child table get selected rows and remove them from item table
    child_items=[]
    to_remove = []
    new_product_bundle_price=0
    all_child_descriptions=''
    for item in qo_items:
        for selected_qo in selected_qo_items:
            if item.name==selected_qo:
                child_items.append({"item_code":item.item_code,"qty":item.qty,"description":item.description,"uom":item.stock_uom})
                to_remove.append(item)
                new_product_bundle_price += item.base_net_amount
                all_child_descriptions+="<div>"+item.description+"</div>"
    [quotation.remove(d) for d in to_remove]

    # create new product bundle with parent item and selected child items
    product_bundle=frappe.get_doc({
        'doctype': 'Product Bundle',
        'new_item_code': new_product_bundle_name,
        'items': child_items
    }).insert(ignore_permissions = True)    

    # check if item price exists
    Item_prices = frappe.get_all('Item Price',filters={
        'item_code':new_product_bundle_name,
        'price_list':quotation.selling_price_list
    })
    # create item price if it doesn't exist
    if len(Item_prices)==0:
        Item_price = frappe.new_doc('Item Price')
        Item_price.item_code = new_product_bundle_name
        Item_price.price_list=quotation.selling_price_list
        Item_price.price_list_rate=new_product_bundle_price
        Item_price.insert(ignore_permissions = True)        

    # update rate in parent item
    description=new_product_bundle_item.description+all_child_descriptions
    new_product_bundle_item.update({
        "standard_rate":new_product_bundle_price,
        "description":description
    })
    new_product_bundle_item.save()

    # add newly created product bundle
    row = quotation.append('items', {})
    row.item_code = new_product_bundle_name
    row.qty=1
    row.rate=new_product_bundle_price
    row.price_list_rate=new_product_bundle_price

    index=1
    for item in qo_items:
        item.idx=index
        index=index+1

    quotation.run_method("set_missing_values")
    quotation.run_method("calculate_taxes_and_totals")
    quotation.save()
    return 1