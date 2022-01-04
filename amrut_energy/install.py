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
            )
        ],
        "Delivery Note Item": [
            dict(
                fieldname="issue_cf",
                label="Issue",
                fieldtype="Link",
                translatable=0,
                options="Issue",
            )
        ],
    }

    create_custom_fields(custom_fields)
