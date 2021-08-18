# -*- coding: utf-8 -*-
# Copyright (c) 2020, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe


def on_validate_contact(doc, method):
    if not doc.phone:
        if doc.phone_nos:
            doc.phone_nos[0].is_primary_phone = 1
