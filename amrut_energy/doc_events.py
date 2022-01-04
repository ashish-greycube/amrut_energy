# -*- coding: utf-8 -*-
# Copyright (c) 2020, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt, getdate, nowdate, add_days, today
from erpnext import get_company_currency, get_default_company


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
            if not contact_phone and doc.party_type == "Customer":
                contact_phone = frappe.db.get_value("Customer", doc.party, "mobile_no")
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
