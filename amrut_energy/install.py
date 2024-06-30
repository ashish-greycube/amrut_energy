# -*- coding: utf-8 -*-
# Copyright (c) 2020, GreyCube Technologies and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.desk.page.setup_wizard.setup_wizard import make_records


def after_migrate():

    custom_fields = {
        "Sales Order": [
            dict(
                fieldname="issue_cf",
                label="Issue",
                fieldtype="Link",
                translatable=0,
                options="Issue",
                insert_after="order_type",
            )
        ],
        "Delivery Note Item": [
            dict(
                fieldname="issue_cf",
                label="Issue",
                fieldtype="Link",
                translatable=0,
                options="Issue",
                insert_after="dn_detail",
            )
        ],
        "Serial No": [
            {
                "label": "Purchase / Manufacture Details",
                "fieldname": "custom_purchase__manufacture_details",
                "insert_after": "purchase_rate",
                "fieldtype": "Section Break",
            },
            {
                "label": "Creation Document Type",
                "fieldname": "custom_creation_document_type",
                "insert_after": "custom_purchase__manufacture_details",
                "fieldtype": "Link",
                "options": "DocType",
            },
            {
                "label": "Creation Date",
                "fieldname": "custom_creation_date",
                "insert_after": "custom_creation_document_type",
                "fieldtype": "Date",
            },
            {
                "label": "Supplier",
                "fieldname": "custom_supplier",
                "insert_after": "custom_creation_date",
                "fieldtype": "Link",
                "options": "Supplier",
            },
            {
                "fieldname": "custom_column_break_qm4kv",
                "insert_after": "custom_supplier",
                "fieldtype": "Column Break",
            },
            {
                "label": "Creation Document No",
                "fieldname": "custom_creation_document_no",
                "insert_after": "custom_column_break_qm4kv",
                "fieldtype": "Dynamic Link",
                "options": "custom_creation_document_type",
            },
            {
                "label": "Creation Time",
                "fieldname": "custom_creation_time",
                "insert_after": "custom_creation_document_no",
                "fieldtype": "Time",
            },
            {
                "label": "Delivery Details",
                "fieldname": "custom_delivery_details",
                "insert_after": "custom_creation_time",
                "fieldtype": "Section Break",
            },
            {
                "label": "Delivery Document Type",
                "fieldname": "custom_delivery_document_type",
                "insert_after": "custom_delivery_details",
                "fieldtype": "Link",
                "options": "DocType",
            },
            {
                "label": "Delivery Date",
                "fieldname": "custom_delivery_date",
                "insert_after": "custom_delivery_document_type",
                "fieldtype": "Date",
            },
            {
                "label": "Customer",
                "fieldname": "custom_customer",
                "insert_after": "custom_delivery_date",
                "fieldtype": "Link",
                "options": "Customer",
            },
            {
                "fieldname": "custom_column_break_1hncq",
                "insert_after": "custom_customer",
                "fieldtype": "Column Break",
            },
            {
                "label": "Delivery Document No",
                "fieldname": "custom_delivery_document_no",
                "insert_after": "custom_column_break_1hncq",
                "fieldtype": "Dynamic Link",
                "options": "custom_delivery_document_type",
            },
            {
                "label": "Delivery Time",
                "fieldname": "custom_delivery_time",
                "insert_after": "custom_delivery_document_no",
                "fieldtype": "Time",
            },
            {
                "label": "Territory",
                "fieldname": "custom_territory",
                "insert_after": "custom_delivery_time",
                "fieldtype": "Link",
                "options": "Territory",
            },
            {
                "label": "Invoice Details",
                "fieldname": "custom_invoice_details",
                "insert_after": "custom_territory",
                "fieldtype": "Section Break",
            },
            {
                "label": "Sales Invoice",
                "fieldname": "custom_sales_invoice",
                "insert_after": "custom_invoice_details",
                "fieldtype": "Link",
                "options": "Sales Invoice",
            },
            {
                "label": "Warranty Period Days",
                "fieldname": "custom_warranty_period_days",
                "insert_after": "warranty_period",
                "fieldtype": "Int",
            },
        ],
    }

    create_custom_fields(custom_fields)
