# -*- coding: utf-8 -*-
# Copyright (c) 2020, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt, getdate, nowdate, add_days, today, get_url, cstr, cint
from erpnext import get_company_currency, get_default_company
from frappe.utils.file_manager import MaxFileSizeReachedError
import re

# from erpnext.regional.india.utils import validate_gstin_check_digit
from india_compliance.gst_india.utils import validate_gstin_check_digit
from frappe.utils.csvutils import getlink
from frappe.utils import get_link_to_form
import erpnext


def on_validate_contact(doc, method):
    if not doc.phone:
        if doc.phone_nos:
            doc.phone_nos[0].is_primary_phone = 1


def on_validate_payment_entry(doc, method):
    contact_phone = doc.contact_phone
    if not contact_phone:
        if doc.references:
            ref = doc.references[-1]
            reference_doctype = ref.get("reference_doctype")
            contact_phone = frappe.db.get_value(
                reference_doctype, ref.name, "contact_mobile"
            )
            if not contact_phone and doc.get("party_type") in ["Customer", "Supplier"]:
                contact_phone = frappe.db.get_value(
                    doc.party_type, doc.party, "mobile_no"
                )
        else:
            if not contact_phone and doc.get("party_type") in ["Customer", "Supplier"]:
                contact_phone = frappe.db.get_value(
                    doc.party_type, doc.party, "mobile_no"
                )
        if contact_phone:
            doc.contact_phone = contact_phone


def on_validate_issue(doc, method):
    contact_number = doc.contact_number
    if not contact_number:
        if doc.customer:
            contact_number = frappe.db.get_value("Customer", doc.customer, "mobile_no")
        if not contact_number:
            if doc.contact:
                contact_number = frappe.db.get_value(
                    "Contact", doc.contact, "mobile_no"
                )
        if contact_number:
            doc.contact_number = contact_number
        else:
            frappe.throw("Contact Number is mandatory for Issue.")


@frappe.whitelist()
def make_sales_order(source_name, target_doc=None, ignore_permissions=True):
    def set_missing_values(source, target):
        target.customer = source.customer
        target.customer_name = source.customer_name
        target.order_type = "Repair"
        target.delivery_date = add_days(today(), 2)
        target.issue_cf = source_name

        target.ignore_pricing_rule = 1
        target.flags.ignore_permissions = ignore_permissions
        target.run_method("set_missing_values")
        target.run_method("calculate_taxes_and_totals")

    doclist = get_mapped_doc(
        "Issue",
        source_name,
        {
            "Issue": {
                "doctype": "Sales Order",
                # "validation": {"docstatus": ["=", 1]},
            },
            "Sales Taxes and Charges": {
                "doctype": "Sales Taxes and Charges",
                "add_if_empty": True,
            },
            "Sales Team": {"doctype": "Sales Team", "add_if_empty": True},
            "Payment Schedule": {"doctype": "Payment Schedule", "add_if_empty": True},
        },
        target_doc,
        set_missing_values,
        ignore_permissions=ignore_permissions,
    )

    return doclist


def on_submit_sales_order(doc, method):
    if doc.issue_cf:
        issue = frappe.get_doc("Issue", doc.issue_cf)
        issue.status = "Closed"
        issue.flags.ignore_permissions = True
        issue.flags.ignore_mandatory = True
        issue.save()
        frappe.db.commit()


def on_insert_quotation_for_engati_chat_generate_PDF(self, method):
    engati_user = frappe.db.get_single_value(
        "Amrut Settings", "default_api_user_for_engati"
    )
    print_format = frappe.db.get_single_value(
        "Amrut Settings", "pdf_print_format_for_url"
    )
    if (
        frappe.local.form_dict.get("lead_mobile_no")
        and engati_user == frappe.session.user
        and print_format
    ):
        print_letterhead = True
        if print_format:
            pdf_url = attach_print(
                frappe.get_doc("Quotation", self.name),
                print_format=print_format,
                print_letterhead=print_letterhead,
                file_name=(self.doc_pdf_url_cf.rsplit("/", 1)[1]).split(".pdf")[0],
            )


def on_validate_quotation_for_engati_chat_bot(self, method):
    engati_user = frappe.db.get_single_value(
        "Amrut Settings", "default_api_user_for_engati"
    )
    if (
        frappe.local.form_dict.get("lead_mobile_no")
        and engati_user == frappe.session.user
    ):
        self.quotation_to = "Lead"
        party_name = frappe.db.get_list(
            "Lead", filters={"mobile_no": self.lead_mobile_no}, pluck="name"
        )
        if len(party_name) > 0:
            self.party_name = party_name[0]
            self.tc_name = frappe.db.get_single_value(
                "Amrut Settings", "quotation_tc_chatbot"
            )
            self.terms = frappe.db.get_value(
                "Terms and Conditions", self.tc_name, "terms"
            )
            doc_pdf_url_cf = "{0}_{1}_{2}.pdf".format(
                "Quotation", self.name, frappe.generate_hash(length=8)
            )
            self.doc_pdf_url_cf = cstr(get_url("/files/" + doc_pdf_url_cf))
        else:
            frappe.throw(
                _("Lead doesnot exist for mobile no {0}".format(self.lead_mobile_no))
            )


def attach_print(
    doc,
    file_name=None,
    print_format=None,
    style=None,
    html=None,
    lang=None,
    print_letterhead=True,
    password=None,
):
    """Save print as an attachment in given document."""
    if not file_name:
        file_name = "{0}_{1}_{2}".format(
            doc.doctype, doc.name, frappe.generate_hash(length=8)
        )
    quotation = frappe.get_doc(doc.doctype, doc.name)
    out = frappe.attach_print(
        doc.doctype,
        doc.name,
        file_name,
        print_format,
        style,
        html,
        quotation,
        lang,
        print_letterhead,
        password,
    )

    try:
        _file = frappe.get_doc(
            {
                "doctype": "File",
                "file_name": out["fname"],
                "attached_to_doctype": doc.doctype,
                "attached_to_name": doc.name,
                "is_private": 0,
                "content": out["fcontent"],
            }
        )
        _file.save(ignore_permissions=True)
        frappe.db.commit()
        return file_name

    except MaxFileSizeReachedError:
        # WARNING: bypass max file size exception
        pass
    except frappe.FileAlreadyAttachedException:
        pass
    except frappe.DuplicateEntryError:
        # same file attached twice??
        pass


def on_validate_supplier(doc, method):
    validate_gstin_for_tax_id(doc, method)


def on_validate_customer(doc, method):
    validate_gstin_for_tax_id(doc, method)


def validate_gstin_for_tax_id(doc, method):
    # validate unique

    GSTIN_FORMAT = re.compile(
        "^[0-9]{2}[A-Z]{4}[0-9A-Z]{1}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}[1-9A-Z]{1}[0-9A-Z]{1}$"
    )

    if not hasattr(doc, "tax_id") or not doc.tax_id:
        return

    doc.tax_id = doc.tax_id.upper().strip()
    if not doc.tax_id or doc.tax_id == "NA":
        return

    existing_tax_id = frappe.db.get_all(
        doc.doctype,
        filters={"name": ["!=", doc.name], "tax_id": ["=", doc.tax_id]},
        fields=["name"],
    )
    print("existing_tax_id", existing_tax_id)
    if len(existing_tax_id) > 0:
        frappe.throw(
            _(
                "GSTIN is already used in {0}.".format(
                    getlink(doc.doctype, existing_tax_id[0].name)
                )
            ),
            title=_("Duplicate Tax ID(GSTIN)"),
        )

    if len(doc.tax_id) != 15:
        frappe.throw(
            _("A GSTIN must have 15 characters."), title=_("Invalid Tax ID(GSTIN)")
        )

    if len(doc.tax_id) != 15:
        frappe.throw(
            _("A GSTIN must have 15 characters."), title=_("Invalid Tax ID(GSTIN)")
        )

    if not GSTIN_FORMAT.match(doc.tax_id):
        frappe.throw(
            _("The input you've entered doesn't match the format of GSTIN."),
            title=_("Invalid Tax ID(GSTIN)"),
        )

    validate_gstin_check_digit(doc.tax_id)


def on_validate_delivery_note(doc, method):
    """Deprecated. Use wms_mobile on_validate_delivery_note"""
    return
    if doc.is_new():

        # update serial no from sales order item if present
        so_detail = [d.so_detail for d in doc.items if d.so_detail]
        if so_detail:
            for d in frappe.db.sql(
                """
                select 
                    serial_no , item_code , parent_detail_docname , parent  
                from `tabPacked Item` tpi 
                where tpi.parenttype = 'Sales Order' and nullif(serial_no,'') is not null
                and parent_detail_docname in ({})
            """.format(
                    ",".join(["%s"] * len(so_detail))
                ),
                tuple(so_detail),
                as_dict=True,
            ):
                for item in doc.packed_items:
                    so_detail = [
                        i.so_detail
                        for i in doc.items
                        if i.name == item.parent_detail_docname
                    ]
                    if (
                        so_detail
                        and so_detail[0] == d.parent_detail_docname
                        and item.item_code == d.item_code
                    ):

                        item.serial_no = d.serial_no


def on_before_insert_stock_entry(self, method):
    if self.purpose == "Manufacture" and self.bom_no:
        bom = frappe.get_doc("BOM", self.bom_no)
        bom_qty = bom.quantity
        se_qty = self.fg_completed_qty
        for bom_row in bom.get("additional_cost_cf"):
            se_additional_cost = self.append("additional_costs", {})
            se_additional_cost.expense_account = bom_row.expense_account
            se_additional_cost.description = bom_row.description
            se_additional_cost.exchange_rate = 1
            se_additional_cost.amount = (se_qty / bom_qty) * bom_row.amount
            se_additional_cost.base_amount = (se_qty / bom_qty) * bom_row.amount
            frappe.msgprint(
                _("Additional cost {0} for account {1} is added from BOM").format(
                    se_additional_cost.amount, se_additional_cost.expense_account
                ),
                alert=True,
            )


@frappe.whitelist()
def on_submit_payment_entry_create_inter_company_je(docname, receiving_company_cf):
    self = frappe.get_doc("Payment Entry", docname)
    if receiving_company_cf == None:
        msg = _("Receiving Company is not defined.")
        frappe.throw(msg)
    if (
        self.create_inter_company_journal_entry_cf == 0
        and self.payment_type == "Receive"
    ):
        frappe.db.set_value(
            "Payment Entry", docname, "receiving_company_cf", receiving_company_cf
        )
        frappe.db.set_value(
            "Payment Entry", docname, "create_inter_company_journal_entry_cf", 1
        )

        voucher_type = "Inter Company Journal Entry"
        precision = frappe.get_precision(
            "Journal Entry Account", "debit_in_account_currency"
        )
        sending_inter_company_journal_entry_reference = None
        receiving_inter_company_journal_entry_reference = None

        # receiving_bank_account_list=frappe.db.get_list('Inter Company Settings Mapping CT',filters={
        #                         'sending_company': self.company,
        #                         'sending_bank_account':self.paid_to,
        #                         'receiving_company':receiving_company_cf
        #                         },fields=['receiving_bank_account'])
        receiving_bank_account_list = frappe.db.get_list(
            "Account",
            filters={
                "account_name": frappe.db.get_value(
                    "Account", self.paid_to, "account_name"
                ),
                "account_type": "Bank",
                "company": receiving_company_cf,
            },
            fields=["name"],
        )
        # if len(receiving_bank_account_list)<1:
        #     msg = _('There is no inter company mapping. Please set at {0}'
        #             .format(frappe.bold(get_link_to_form('Inter Company Settings CD','Inter Company Settings CD'))))
        #     frappe.throw(msg)
        if len(receiving_bank_account_list) < 1:
            receiving_bank_account = None
        else:
            receiving_bank_account = receiving_bank_account_list[0].name

        if len(receiving_bank_account_list) < 1 or not receiving_bank_account:
            msg = _(
                "Receiving company bank account mapping is not found . <br> It is not found for Sending Company: {0}, Sending Bank Account: {1} & Receiving Company: {2}.".format(
                    self.company, self.paid_to, receiving_company_cf
                )
            )
            frappe.throw(msg)
        receiving_company_cost_center = frappe.db.get_value(
            "Company", self.company, "cost_center"
        )
        if not receiving_company_cost_center:
            msg = _(
                "Default cost center is not set for company {0}.".format(
                    frappe.bold(get_link_to_form("Company", self.company))
                )
            )
            frappe.throw(msg)
        default_company_credit_account = frappe.db.get_value(
            "Company", self.company, "default_payable_account"
        )
        if not default_company_credit_account:
            msg = _(
                "Default payable account is not set for company {0}.".format(
                    frappe.bold(get_link_to_form("Company", self.company))
                )
            )
            frappe.throw(msg)
        credit_supplier_list = frappe.db.get_list(
            "Supplier",
            filters={
                "represents_company": receiving_company_cf,
                "is_internal_supplier": 1,
            },
            fields=["name"],
        )
        if len(credit_supplier_list) < 1:
            msg = _(
                "There is no internal supplier set for receiving company {0}. Please create an internal suppplier for this company.".format(
                    receiving_company_cf
                )
            )
            frappe.throw(msg)
        credit_supplier = credit_supplier_list[0].name

        sending_company_cost_center = None
        if self.cost_center:
            sending_company_cost_center = self.cost_center
        if sending_company_cost_center == None:
            sending_company_cost_center = frappe.db.get_value(
                "Company", self.company, "cost_center"
            )

        # if not sending_company_cost_center:
        #     msg = _('Cost center is not defined in payment entry {0}.'
        #         .format(frappe.bold(get_link_to_form('Payment Entry',self.name))))
        #     frappe.throw(msg)

        receiving_company_cost_center = frappe.db.get_value(
            "Company", receiving_company_cf, "cost_center"
        )
        # if not receiving_company_cost_center:
        #     msg = _('Cost center is not defined in company {0}.'
        #            .format(frappe.bold(get_link_to_form('Company',self.company))))
        #     frappe.throw(msg)

        default_company_debit_account = frappe.db.get_value(
            "Company", receiving_company_cf, "default_receivable_account"
        )
        if not default_company_debit_account:
            msg = _(
                "Default receivable account is not set for company {0}.".format(
                    frappe.bold(get_link_to_form("Company", receiving_company_cf))
                )
            )
            frappe.throw(msg)

        debit_customer_list = frappe.db.get_list(
            "Customer",
            filters={"represents_company": self.company, "is_internal_customer": 1},
            fields=["name"],
        )
        if len(debit_customer_list) < 1:
            msg = _(
                "There is no internal customer set for sending company {0}. Please create an internal customer for this company.".format(
                    self.company
                )
            )
            frappe.throw(msg)
        debit_customer = debit_customer_list[0].name

        try:
            # sending company : i.e. branch
            sending_accounts = []
            # credit entry
            sending_accounts.append(
                {
                    "account": self.paid_to,
                    "credit_in_account_currency": flt(self.paid_amount, precision),
                    "cost_center": sending_company_cost_center or "",
                }
            )
            # debit entry
            sending_accounts.append(
                {
                    "account": default_company_credit_account,
                    "party_type": "Supplier",
                    "party": credit_supplier,
                    "debit_in_account_currency": flt(self.paid_amount, precision),
                    "cost_center": sending_company_cost_center or "",
                }
            )
            sending_journal_entry = frappe.new_doc("Journal Entry")
            sending_journal_entry.voucher_type = voucher_type
            sending_journal_entry.user_remark = _("{0}").format(self.name)
            sending_journal_entry.company = self.company
            sending_journal_entry.posting_date = self.posting_date
            sending_journal_entry.set("accounts", sending_accounts)
            sending_journal_entry.save(ignore_permissions=True)
            sending_journal_entry.submit()

            # receiving company : i.e. head office
            receiving_accounts = []
            # credit entry
            receiving_accounts.append(
                {
                    "account": default_company_debit_account,
                    "party_type": "Customer",
                    "party": debit_customer,
                    "credit_in_account_currency": flt(self.paid_amount, precision),
                    "cost_center": receiving_company_cost_center or "",
                }
            )
            # debit entry
            receiving_accounts.append(
                {
                    "account": receiving_bank_account,
                    "debit_in_account_currency": flt(self.paid_amount, precision),
                    "cost_center": receiving_company_cost_center or "",
                }
            )
            receiving_journal_entry = frappe.new_doc("Journal Entry")
            receiving_journal_entry.voucher_type = voucher_type
            receiving_journal_entry.user_remark = _("{0}").format(self.name)
            receiving_journal_entry.company = receiving_company_cf
            receiving_journal_entry.posting_date = self.posting_date
            receiving_journal_entry.set("accounts", receiving_accounts)
            receiving_journal_entry.inter_company_journal_entry_reference = (
                sending_journal_entry.name
            )
            receiving_journal_entry.save(ignore_permissions=True)
            receiving_journal_entry.submit()

            frappe.db.set_value(
                "Journal Entry",
                sending_journal_entry.name,
                "inter_company_journal_entry_reference",
                receiving_journal_entry.name,
            )

            msg = _(
                "Receiving Company Journal Entry {0} is created.".format(
                    frappe.bold(
                        get_link_to_form("Journal Entry", receiving_journal_entry.name)
                    )
                )
            )
            frappe.msgprint(msg)

            msg = _(
                "Sending Company Journal Entry {0} is created.".format(
                    frappe.bold(
                        get_link_to_form("Journal Entry", sending_journal_entry.name)
                    )
                )
            )
            frappe.msgprint(msg)

        except Exception:
            frappe.throw(frappe.get_traceback())


# def on_cancel_payment_entry_delete_inter_company_je(self,method):
#     journal_entry_list=frappe.db.get_list('Journal Entry',filters={
#     'user_remark': self.name},fields=['name'])
#     if len(journal_entry_list)>0:
#         for je in journal_entry_list:
#             doc = frappe.get_doc('Journal Entry', je.name)
#             if doc.docstatus==1:
#                 doc.cancel()
#                 doc.delete()
#                 msg = _('Journal Entry {0} is deleted.'.format(frappe.bold(je.name)))
#                 frappe.msgprint(msg)
#             # doc = frappe.get_doc('Journal Entry', je.name)

# def on_cancel_je_delete_corresponding_inter_company_je(self,method):
#     inter_company_journal_entry_reference = frappe.db.get_value('Journal Entry', self.name, 'inter_company_journal_entry_reference')
#     print('inter_company_journal_entry_reference',inter_company_journal_entry_reference)
#     if inter_company_journal_entry_reference:
#         doc = frappe.get_doc('Journal Entry', inter_company_journal_entry_reference)
#         if doc.docstatus==1:
#             doc.cancel()
#             doc.delete()
#             # frappe.delete_doc('Journal Entry', inter_company_journal_entry_reference)
#             msg = _('Journal Entry {0} is deleted.'.format(frappe.bold(inter_company_journal_entry_reference)))
#             frappe.msgprint(msg)


def on_submit_serial_and_batch_bundle(doc, method):
    try:
        _on_submit_serial_and_batch_bundle(doc, method)
    except Exception as e:
        frappe.log_error(
            title="on_submit_serial_and_batch_bundle: Serial No Customization",
            message=frappe.get_traceback(),
        )


def _on_submit_serial_and_batch_bundle(doc, method):
    # set serial no values from S&BB
    # doc = frappe.get_doc("Serial and Batch Bundle", frappe.form_dict["name"])

    if not cint(
        frappe.db.get_single_value(
            "Amrut Settings", "update_serial_no_from_serial_and_batch_bundle"
        )
    ):
        return

    def handle_return(type_of_transaction, entries):
        clear_fields = ()
        if type_of_transaction == "Outward":
            clear_fields = (
                "custom_creation_document_type",
                "custom_creation_document_no",
                "custom_creation_date",
                "custom_creation_time",
            )
        elif type_of_transaction == "Inward":
            clear_fields = (
                "custom_delivery_document_type",
                "custom_delivery_document_no",
                "custom_delivery_date",
                "custom_delivery_time",
                "warranty_period",
                "custom_warranty_period_days",
                "warranty_expiry_date",
                "maintenance_status",
                "custom_customer",
                "custom_territory",
            )

        for d in entries:
            serial_no_doc = frappe.get_doc("Serial No", d.serial_no)
            for d in clear_fields:
                if serial_no_doc.get(d):
                    serial_no_doc.set(d, None)

            if doc.voucher_type in ["Purchase Receipt", "Purchase Invoice"]:
                if serial_no_doc.custom_supplier:
                    serial_no_doc.set("custom_supplier", None)

            serial_no_doc.save()

    if doc.voucher_type in (
        "Purchase Receipt",
        "Delivery Note",
    ) and frappe.db.get_value(doc.voucher_type, doc.voucher_no, "is_return"):
        handle_return(doc.type_of_transaction, doc.entries)

    else:

        for d in doc.entries:
            serial_no_doc = frappe.get_doc("Serial No", d.serial_no)

            if doc.type_of_transaction == "Inward":
                if not serial_no_doc.custom_creation_document_type:
                    serial_no_doc.custom_creation_document_type = doc.voucher_type
                if not serial_no_doc.custom_creation_document_no:
                    serial_no_doc.custom_creation_document_no = doc.voucher_no
                if not serial_no_doc.custom_creation_date:
                    serial_no_doc.custom_creation_date = doc.posting_date
                if not serial_no_doc.custom_creation_time:
                    serial_no_doc.custom_creation_time = doc.posting_time

                if doc.voucher_type in ["Purchase Receipt", "Purchase Invoice"]:
                    supplier = frappe.db.get_value(
                        doc.voucher_type, doc.voucher_no, "supplier"
                    )
                    if supplier:
                        serial_no_doc.custom_supplier = supplier

            elif doc.type_of_transaction == "Outward":
                serial_no_doc.custom_delivery_document_type = doc.voucher_type
                serial_no_doc.custom_delivery_document_no = doc.voucher_no
                serial_no_doc.custom_delivery_date = doc.posting_date
                serial_no_doc.custom_delivery_time = doc.posting_time

                if doc.voucher_type in ["Delivery Note", "Sales Invoice"]:
                    customer = frappe.db.get_value(
                        doc.voucher_type, doc.voucher_no, "customer"
                    )
                    serial_no_doc.custom_customer = customer

                    territory = frappe.db.get_value("Customer", customer, "territory")
                    serial_no_doc.custom_territory = territory

            if doc.voucher_type == "Delivery Note" and doc.voucher_no:
                # Set Sales Invoice
                # In case SI is created , then DN is created..
                # Reverse scenario i.e. DN created first later SI created , is handled in on_submit SI doc_event
                for d in frappe.db.sql(
                    """
                    select tsii.parent sales_invoice 
                    from `tabSerial and Batch Bundle` tsabb 
                    inner join `tabSales Invoice Item` tsii on tsii.delivery_note = tsabb.voucher_no  
                    where tsabb.name = %s
                """,
                    (doc.name),
                ):
                    serial_no_doc.custom_sales_invoice = d[0]

                for d in frappe.db.sql(
                    """
                    select 
                        tdni.custom_warranty_period 
                    from `tabDelivery Note Item` tdni  
                    left outer join `tabPacked Item` tpi
                    on tpi.parenttype = 'Delivery Note' and tpi.parent_detail_docname = tdni.name  
                        and tpi.parent = tdni.parent
                    where tdni.name = %s
                        and COALESCE(tdni.custom_warranty_period,0) > 0
                """,
                    (doc.voucher_detail_no,),
                ):
                    warranty_period = frappe.utils.cint(d[0])

                    serial_no_doc.custom_warranty_period_days = warranty_period
                    serial_no_doc.warranty_period = (
                        warranty_period  # gets overwritten by erpnext
                    )
                    serial_no_doc.warranty_expiry_date = frappe.utils.add_days(
                        doc.posting_date, warranty_period
                    )
                    serial_no_doc.maintenance_status = "Under Warranty"

            serial_no_doc.save()


def on_cancel_serial_and_batch_bundle(doc, method):
    if not cint(
        frappe.db.get_single_value(
            "Amrut Settings", "update_serial_no_from_serial_and_batch_bundle"
        )
    ):
        return
    try:
        for d in doc.entries:
            serial_no_doc = frappe.get_doc("Serial No", d.serial_no)
            if doc.voucher_type == "Purchase Receipt":
                for field in [
                    "custom_creation_document_type",
                    "custom_creation_document_no",
                    "custom_creation_date",
                    "custom_creation_time",
                    "custom_supplier",
                ]:
                    serial_no_doc.set(field, None)
            elif doc.voucher_type == "Delivery Note":
                for field in [
                    "custom_delivery_document_type",
                    "custom_delivery_document_no",
                    "custom_delivery_date",
                    "custom_delivery_time",
                    "custom_customer",
                    "custom_territory",
                    "warranty_period",
                    "custom_warranty_period_days",
                    "warranty_expiry_date",
                    "maintenance_status",
                ]:
                    serial_no_doc.set(field, None)

            if doc.voucher_type in ["Purchase Receipt", "Purchase Invoice"]:
                if serial_no_doc.custom_supplier:
                    serial_no_doc.set("custom_supplier", None)

            serial_no_doc.save()
    except Exception as e:
        frappe.log_error(
            title="on_cancel_serial_and_batch_bundle: Serial No Customization",
            message=frappe.get_traceback(),
        )


def on_submit_sales_invoice(doc, method):
    # for scenario where DN created first , then SI created, on_submit SI doc_event to handle
    if not cint(
        frappe.db.get_single_value(
            "Amrut Settings", "update_serial_no_from_serial_and_batch_bundle"
        )
    ):
        return

    try:

        for d in doc.items:
            if d.delivery_note:
                for sabb in frappe.db.get_all(
                    "Serial and Batch Bundle",
                    {"voucher_type": "Delivery Note", "voucher_no": d.delivery_note},
                ):
                    sabb_doc = frappe.get_doc("Serial and Batch Bundle", sabb.name)
                    for ent in sabb_doc.entries:
                        frappe.db.set_value(
                            "Serial No", ent.serial_no, "custom_sales_invoice", doc.name
                        )
    except Exception as e:
        frappe.log_error(
            title="on_submit_sales_invoice: Serial No Customization",
            message=frappe.get_traceback(),
        )


@frappe.whitelist()
def update_serial_no_from_serial_and_batch_bundle(start, end):
    # update previous records with S&BB
    for d in frappe.get_all(
        "Serial and Batch Bundle",
        filters={"creation": ["between", (start, end)]},
        fields=["name", "docstatus"],
        order_by="creation asc",
    ):
        print(d.name)
        if d.docstatus == 1:
            on_submit_serial_and_batch_bundle(
                doc=frappe.get_doc("Serial and Batch Bundle", d.name), method=None
            )
        elif d.docstatus == 2:
            on_cancel_serial_and_batch_bundle(
                doc=frappe.get_doc("Serial and Batch Bundle", d.name), method=None
            )


@frappe.whitelist()
def update_serial_no_from_sales_invoice(start, end):
    # update previous records with S&BB
    frappe.db.sql(
        """
        update `tabSales Invoice Item` tsii 
        inner join `tabSales Invoice` tsi on tsi.name = tsii.parent and tsi.docstatus = 1
        inner join `tabSerial and Batch Bundle` tsabb on tsabb.voucher_no = tsii.delivery_note 
            and tsabb.voucher_type = 'Delivery Note'
        inner join `tabSerial and Batch Entry` tsabe on tsabe.parent = tsabb.name 
        inner join `tabSerial No` tsn on tsn.name = tsabe.serial_no 
        set tsn.custom_sales_invoice = tsi.name
        where delivery_note is not null
                  """
    )


@frappe.whitelist()
def update_serial_no_from_pr(start, end):
    for d in frappe.db.sql(
        """
    select 
        tpri.serial_no, tpri.item_code , tpr.name , tpr.supplier ,
        tpr.posting_date , tpr.posting_time
    from `tabPurchase Receipt Item` tpri 
	inner join `tabPurchase Receipt` tpr on tpr.name = tpri.parent
		and tpr.docstatus = 1
	where tpri.serial_and_batch_bundle is null 
        and nullif(tpri.serial_no,'') is not null  
		and tpr.creation BETWEEN %s and %s
                           """,
        (start, end),
        as_dict=True,
        debug=True,
    ):
        print(d.name)
        args = d.serial_no.split("\n")

        frappe.db.sql(
            """
        update `tabSerial No`
        set 
        custom_creation_document_type= 'Purchase Receipt' ,
        custom_creation_document_no= %s ,
        custom_creation_date= %s ,
        custom_creation_time= %s ,
        custom_supplier= %s
        where name in ({})
                      """.format(
                ",".join(["%s"] * len(args))
            ),
            tuple([d.name, d.posting_date, d.posting_time, d.supplier] + args),
        )
        frappe.db.commit()


@frappe.whitelist()
def update_serial_no_from_dn(start, end):
    for d in frappe.db.sql(
        """
	select tdni.serial_no , tdni.item_code , tdn.name ,
		tdn.posting_date , tdn.posting_time , tdn.customer , tc.territory 
	from `tabDelivery Note Item` tdni 
	inner join `tabDelivery Note` tdn on tdn.name = tdni.parent 
		and tdn.docstatus = 1
    inner join tabCustomer tc on tc.name = tdn.customer        
	where tdni.serial_and_batch_bundle is null 
        and nullif(tdni.serial_no ,'') is not null		
    and tdn.creation BETWEEN %s and %s
                           """,
        (start, end),
        as_dict=True,
    ):
        print(d.name)
        args = d.serial_no.split("\n")

        print(args)

        frappe.db.sql(
            """
        update `tabSerial No`
        set 
            custom_delivery_document_type= 'Delivery Note' ,
            custom_delivery_document_no= %s ,
            custom_delivery_date = %s ,
            custom_delivery_time = %s ,
            custom_customer = %s ,
            custom_territory = %s
        where name in ({})
                     """.format(
                ",".join(["%s"] * len(args))
            ),
            tuple(
                [d.name, d.posting_date, d.posting_time, d.customer, d.territory] + args
            ),
        ),
        frappe.db.commit()


@frappe.whitelist()
def update_serial_no_set_sales_invoice(start, end):
    for d in frappe.db.sql(
        """
        select 
            tsii.parent , tdni.serial_no 
        from `tabSales Invoice Item` tsii 
        inner join `tabSales Invoice` tsi on tsi.name = tsii.parent
            and tsi.docstatus = 1
        inner join `tabDelivery Note Item` tdni on tdni.name = tsii.dn_detail 
            and nullif(tdni.serial_no,'') is not null 
            and tdni.serial_and_batch_bundle is null
        where tsii.delivery_note is not null
                           """,
        as_dict=True,
    ):
        args = d.serial_no.split("\n")
        print(d.parent)
        frappe.db.sql(
            """
        update `tabSerial No`
        set 
            custom_sales_invoice = %s
        where nullif(custom_sales_invoice,'') is null and name in ({})
                      """.format(
                ",".join(["%s"] * len(args))
            ),
            tuple([d.parent] + args),
        )
    frappe.db.commit()
