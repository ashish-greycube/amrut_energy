# -*- coding: utf-8 -*-
# Copyright (c) 2020, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
import requests
import jwt
import uuid
import datetime


videosdk_api_url = "https://api.videosdk.live/v1/meetings"

# https://docs.videosdk.live/docs/realtime-communication/sdk-reference/prebuilt-sdk-js/setup/


@frappe.whitelist(allow_guest=True)
def generate_token():
    conf = frappe._dict(frappe.conf.videosdk)
    expires = 24 * 3600
    now = datetime.datetime.utcnow()
    exp = now + datetime.timedelta(seconds=expires)
    token = jwt.encode(
        payload={"apikey": conf.api_key, "permissions": ["allow_join"]},
        key=conf.secret_key,
    ).decode("utf-8")

    print("token: ", token)
    return token


@frappe.whitelist(allow_guest=True)
def create_meeting(**args):
    token = generate_token()
    headers = {"authorization": f"{token}"}
    response = requests.request("POST", videosdk_api_url, headers=headers)

    result = response.json()

    conf = frappe._dict(frappe.conf.videosdk)

    meeting_url = "{}/call?meeting_id={}&api_key={}&meeting_title={}".format(
        frappe.utils.get_site_url(frappe.local.site),
        result.get("meetingId"),
        conf.api_key,
        args.get("subject"),
    )

    return meeting_url


@frappe.whitelist(allow_guest=True)
def validate_meeting(meetingId=""):
    print("*\n" * 25, "meetingId", meetingId)
    print(frappe.form_dict)
    token = generate_token()
    url = videosdk_api_url + "/" + meetingId
    headers = {"authorization": f"{token}"}
    response = requests.request("POST", url, headers=headers)

    print(response.json())
    return response.json()
