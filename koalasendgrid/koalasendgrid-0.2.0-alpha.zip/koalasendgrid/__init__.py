# -*- coding: utf-8 -*-
"""
    koalasendgrid.__init__.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Wrapper around the sendgrid package. Adds event hooks and hides as much of the implementation as possible.

    :copyright: (c) 2015 Lighthouse
    :license: LGPL
"""

import config
import sendgrid
from sendgrid.helpers.mail import *

__author__ = 'Matt'


api_key = config.secrets.get('sendgrid_api_key')
SENDGRID_CLIENT = sendgrid.SendGridAPIClient(apikey=api_key)

DEFAULT_SUBJECT = config.secrets.get('sendgrid_default_subject')
DEFAULT_FROM_ADDRESS = config.secrets.get('sendgrid_from_address')
DEFAULT_FROM_NAME = config.secrets.get('sendgrid_from_name')
AUTOMATIC_BCC = config.secrets.getlist('sendgrid_automatic_bcc')


def send_email(to_address, body, subject=DEFAULT_SUBJECT, to_name=None, from_address=DEFAULT_FROM_ADDRESS,
               from_name=DEFAULT_FROM_NAME, html=True, attachment_name=None, attachment_content_buffer=None,
               additional_bcc=None):

    message = Mail()
    message.set_subject(subject)
    message.set_from(Email(from_address, from_name))

    personalization = Personalization()
    personalization.add_to(Email(to_address, to_name))

    if html:
        message.add_content(Content("text/html", body))
    else:
        message.add_content(Content("text/plain", body))

    for bcc_address in AUTOMATIC_BCC:
        personalization.add_bcc(Email(bcc_address))

    if additional_bcc is not None:
        for bcc_address in additional_bcc:
            personalization.add_bcc(Email(bcc_address))

    message.add_personalization(personalization)

    if attachment_content_buffer and attachment_name:
        attachment = Attachment()
        attachment.set_content(attachment_content_buffer)
        attachment.set_filename(attachment_name)
        attachment.set_disposition("attachment")
        message.add_attachment(attachment)

    return SENDGRID_CLIENT.client.mail.send.post(request_body=message.get())

