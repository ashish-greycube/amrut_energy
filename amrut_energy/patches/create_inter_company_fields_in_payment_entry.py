import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    print("Creating fields for Inter Company JE in Payment Entry...")
    custom_fields = {
        "Payment Entry": [
            dict(
                fieldname="create_inter_company_journal_entry_cf",
                label="Inter Company Journal Entry ?",
                fieldtype="Check",
                default=0,
                depends_on="eval:doc.payment_type=='Receive'",
                insert_after="payment_order_status",
                allow_on_submit=1,
                read_only= 1,
                no_copy= 1,
            ),        
            dict(
                fieldname="receiving_company_cf",
                label="Receiving Company",
                fieldtype="Link",
                options="Company",
                insert_after="create_inter_company_journal_entry_cf",
                depends_on="",
                mandatory_depends_on="",
                allow_on_submit=1,
            )
        ]
    }

    create_custom_fields(custom_fields, update=True)