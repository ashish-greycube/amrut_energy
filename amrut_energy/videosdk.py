# -*- coding: utf-8 -*-
# Copyright (c) 2020, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
import requests
import jwt
import uuid
import datetime


# videosdk_api_url = "https://api.videosdk.live/v1/meetings"

# https://docs.videosdk.live/docs/realtime-communication/sdk-reference/prebuilt-sdk-js/setup/


@frappe.whitelist(allow_guest=True)
def create_meeting(**args):
    frappe.throw("This feature is not supported.")

    settings = frappe.get_single("Amrut Settings")

    token = get_token()
    headers = {"authorization": f"{token}"}
    response = requests.request(
        "POST", settings.videosdk_api_url + "v1/meetings", headers=headers
    )

    result = response.json()

    meeting_url = "{}/call?meeting_id={}&api_key={}&meeting_title={}".format(
        frappe.utils.get_url(),
        result.get("meetingId"),
        settings.videosdk_api_key,
        args.get("subject"),
    )

    return meeting_url


def get_token():
    def _generate_token():
        settings = frappe.get_single("Amrut Settings")
        expires = 24 * 3600
        now = datetime.datetime.utcnow()
        exp = now + datetime.timedelta(seconds=expires)
        token = jwt.encode(
            payload={
                "apikey": settings.videosdk_api_key,
                "permissions": ["allow_join"],
                "exp": exp,
            },
            key=settings.videosdk_secret_key,
        ).decode("utf-8")
        return token

    return frappe.cache().get_value("videosdk_token", _generate_token)


# @frappe.whitelist(allow_guest=True)
# def validate_meeting(meetingId=""):
#     print("*\n" * 25, "meetingId", meetingId)
#     print(frappe.form_dict)
#     token = generate_token()
#     url = videosdk_api_url + "v1/meetings" + meetingId
#     headers = {"authorization": f"{token}"}
#     response = requests.request("POST", url, headers=headers)

#     print(response.json())
#     return response.json()
