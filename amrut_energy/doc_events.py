# -*- coding: utf-8 -*-
# Copyright (c) 2020, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe


def on_validate_contact(doc, method):
    if not doc.phone:
        if doc.phone_nos:
            doc.phone_nos[0].is_primary_phone = 1


def on_validate_payment_entry(doc, method):
    contact_phone =  doc.contact_phone
    if not contact_phone:
        if doc.references:
            ref = doc.references[-1]
            reference_doctype = ref.get("reference_doctype")
            contact_phone = frappe.db.get_value(reference_doctype, ref.name,"contact_mobile")
            if not contact_phone and doc.party_type=="Customer":
                contact_phone = frappe.db.get_value("Customer", doc.party,"mobile_no")
        if contact_phone:
            doc.contact_phone = contact_phone


def on_validate_issue(doc, method):
    contact_number =  doc.contact_number
    if not contact_number:
        if doc.customer:
            contact_number = frappe.db.get_value("Customer", doc.customer, "mobile_no")
        if not contact_number:
            if doc.contact:
                contact_number = frappe.db.get_value("Contact", doc.contact, "mobile_no")
        if contact_number:
            doc.contact_number = contact_number
        else:
            frappe.throw("Contact Number is mandatory for Issue.")
        
