from __future__ import unicode_literals
from frappe import _


def get_data():
    config = [
        {'label': _('Settings'), 
        'items': [
                {
                    "type": "doctype",
                    "name": "Amrut Settings",
                    "description": _("Default settings for Dynamic Product Bundle."),
                    "settings": 1,
                }
            ]
        }
    ]
    return config    