# -*- coding: utf-8 -*-
# Copyright (c) 2020, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt, getdate, nowdate, add_days, today, get_url, cstr
from erpnext import get_company_currency, get_default_company
from frappe.utils.file_manager import MaxFileSizeReachedError
import re
from erpnext.regional.india.utils import validate_gstin_check_digit
from frappe.utils.csvutils import getlink


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
