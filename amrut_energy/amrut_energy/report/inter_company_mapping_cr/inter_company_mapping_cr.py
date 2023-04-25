# Copyright (c) 2023, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data

def get_data(filters):
	data = frappe.db.sql(
        """SELECT  (je.user_remark) as payment_entry,
		je.name as sending_journal_entry,
		je.inter_company_journal_entry_reference as receiving_journal_entry  
		FROM `tabJournal Entry` je 
		where je.voucher_type ='Inter Company Journal Entry' and je.docstatus !=2 and je.user_remark is not null 
		group by je.user_remark  order by je.name ASC            
	""")
	return data

def get_columns(filters):
    columns = [
        {
            "label": _("Payment Entry"),
            "fieldtype": "Link",
            "fieldname": "payment_entry",
            "options": "Payment Entry",
            "width": 280,
        },
        {
            "label": _("Sending Journal Entry"),
            "fieldtype": "Link",
            "fieldname": "sending_journal_entry",
            "options": "Journal Entry",
            "width": 280,
        },
        {
            "label": _("Receiving Journal Entry"),
            "fieldtype": "Link",
            "fieldname": "receiving_journal_entry",
            "options": "Journal Entry",
            "width": 280,
        }]  
    return columns      