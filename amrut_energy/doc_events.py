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
            for d in frappe.db.sql("""
            select
                coalesce(con.mobile_no,cus.mobile_no,'')
                from 
                (select %(party)s party, %(party_type)s party_type) pe
                left outer join `tab{doctype}` d on d.name = %(reference_name)s
                left outer join tabContact con on con.name = d.contact_person
                left outer join tabCustomer cus on cus.name = pe.party and pe.party_type = 'Customer'
            """.format(doctype=reference_doctype), dict(party = doc.party, party_type = doc.party_type, reference_name = ref.name), debug=True):
                contact_phone = d[0]
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
        
