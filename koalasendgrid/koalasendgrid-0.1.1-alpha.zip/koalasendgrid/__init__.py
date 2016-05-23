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

__author__ = 'Matt'


username = config.settings.get('sendgrid_username')
password = config.settings.get('sendgrid_password')
SENDGRID_CLIENT = sendgrid.SendGridClient(username_or_apikey=username, password=password, raise_errors=True)

APP_NAME = config.settings.get('app_name')
DEFAULT_SUBJECT = config.settings.get('sendgrid_default_subject')
DEFAULT_FROM_ADDRESS = config.settings.get('sendgrid_from_address')
DEFAULT_FROM_NAME = config.settings.get('sendgrid_from_name')
AUTOMATIC_BCC = config.settings.getlist('sendgrid_automatic_bcc')


def send_email(to_address, body, subject=DEFAULT_SUBJECT, to_name=None, from_address=DEFAULT_FROM_ADDRESS,
               from_name=DEFAULT_FROM_NAME, html=True, attachment_name=None, attachment_content_buffer=None,
               additional_bcc=None):

    message = sendgrid.Mail()

    if not to_name:
        message.add_to(u'{0}'.format(to_address))
    else:
        message.add_to(u'{0} <{1}>'.format(to_name, to_address))

    message.set_subject(subject)
    if html:
        message.set_html(body)
    else:
        message.set_text(body)

    if not from_name:
        message.set_from(u'{0}'.format(from_address))
    else:
        message.set_from(u'{0} <{1}>'.format(from_name, from_address))

    for bcc_address in AUTOMATIC_BCC:
        message.add_bcc(bcc_address)

    if additional_bcc is not None:
        for bcc in additional_bcc:
            message.add_bcc(bcc)

    if attachment_content_buffer and attachment_name:
        message.add_attachment(attachment_name, attachment_content_buffer)

    return SENDGRID_CLIENT.send(message)

