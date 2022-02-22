# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "amrut_energy"
app_title = "Amrut Energy"
app_publisher = "GreyCube Technologies"
app_description = "Customization for amrut energy company"
app_icon = "octicon octicon-sun"
app_color = "orange"
app_email = "admin@greycube.in"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/amrut_energy/css/amrut_energy.css"
# app_include_js = "/assets/amrut_energy/js/amrut_energy.js"

# include js, css files in header of web template
# web_include_css = "/assets/amrut_energy/css/amrut_energy.css"
# web_include_js = "/assets/amrut_energy/js/amrut_energy.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Item": "public/js/item.js",
    "Quotation": "public/js/quotation.js",
    "Issue": "public/js/issue.js",
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "amrut_energy.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "amrut_energy.install.before_install"
# after_install = "amrut_energy.install.after_install"
after_migrate = "amrut_energy.install.after_migrate"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "amrut_energy.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Contact": {
        "validate": "amrut_energy.doc_events.on_validate_contact",
    },
    "Payment Entry": {
        "validate": "amrut_energy.doc_events.on_validate_payment_entry",
    },
    "Issue": {
        "validate": "amrut_energy.doc_events.on_validate_issue",
    },
    "Sales Order": {
        "on_submit": "amrut_energy.doc_events.on_submit_sales_order",
    },
    "Quotation": {
        "validate": "amrut_energy.doc_events.on_validate_quotation_for_engati_chat_bot",
    }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"amrut_energy.tasks.all"
# 	],
# 	"daily": [
# 		"amrut_energy.tasks.daily"
# 	],
# 	"hourly": [
# 		"amrut_energy.tasks.hourly"
# 	],
# 	"weekly": [
# 		"amrut_energy.tasks.weekly"
# 	]
# 	"monthly": [
# 		"amrut_energy.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "amrut_energy.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "amrut_energy.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "amrut_energy.task.get_dashboard_data"
# }
