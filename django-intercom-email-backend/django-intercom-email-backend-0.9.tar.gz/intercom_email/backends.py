
import logging

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import sanitize_address

from intercom import IntercomError
from intercom.client import Client

logger = logging.getLogger('intercom.email')


class EmailBackend(BaseEmailBackend):

    def __init__(self, fail_silently=False, **kwargs):
        self.fail_silently = fail_silently
        super(EmailBackend, self).__init__(fail_silently=fail_silently)
        self.app_id = settings.INTERCOM_APP_ID
        self.api_key = settings.INTERCOM_API_KEY

        self.client = None

    def open(self):
        if self.client:
            return

        self.client = Client(app_id=self.app_id, api_key=self.api_key)
        try:
            admin_list = self.client.admins.all()
        except IntercomError as err:
            if not self.fail_silently:
                raise
            logger.exception(err.message)

        self.admins = {}
        for admin in admin_list:
            admin_dict = admin.to_dict()
            self.admins[admin_dict['email']] = admin_dict

    def close(self):
        """RESTful API. Nothing to be done here."""
        pass

    def send_messages(self, email_messages):
        """
        Sends one or more EmailMessage objects and returns the number of email
        messages sent.
        """
        if not email_messages:
            return

        self.open()
        if not self.client:
            return

        num_sent = 0
        for message in email_messages:
            num_sent += self._send(message)

    def _send(self, email_message):
        """A helper method that does the actual sending."""

        if not email_message.recipients():
            return False

        from_email = sanitize_address(email_message.from_email,
                                      email_message.encoding)

        recipients = [sanitize_address(addr, email_message.encoding)
                      for addr in email_message.recipients()]

        for to in recipients:
            num_sent = 0
            errors = []
            try:
                self.client.messages.create(**{
                    'message_type': 'email',
                    'subject': email_message.subject,
                    'body': email_message.body,
                    'template': 'plain',
                    'from': {'type': 'admin',
                             'id': self.admins[from_email]['id']},
                    'to': {'type': 'user', 'email': to},
                })
            except IntercomError as err:
                logger.exception('Error sending intercom email: %s - %s (%s)',
                                 err.message, email_message.subject, to)
                errors.append(err)
            else:
                num_sent += 1

        if errors and not self.fail_silently:
            raise errors[0]

        return num_sent
