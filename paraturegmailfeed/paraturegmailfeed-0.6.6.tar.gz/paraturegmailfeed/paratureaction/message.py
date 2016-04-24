"""Module containing class to extract data from Gmail API Message response
into a standard format.
"""


import base64
from datetime import datetime


class ParatureGmailMessage(object):
    """Class modeling Parature Email sent to Gmail"""
    def __init__(self, message):
        self.subject = self._get_subject(message)
        self.body = self._get_body(message)
        self.timestamp = self._get_timestamp(message)

    @staticmethod
    def _get_subject(message):
        """Return str value of subject from Gmail API Message response"""
        headers = message['payload']['headers']

        subject = None
        for header in headers:
            if header['name'] == 'Subject':
                subject = str(header['value'])
                break

        return subject

    @staticmethod
    def _get_body(message):
        """Return str value of body from Gmail API Message response"""
        body_parts = message['payload']['parts']

        original_message = body_parts[1]
        body = original_message['body']['data']

        decoded_body = base64.urlsafe_b64decode(str(body))

        return decoded_body

    def _get_timestamp(self, message):
        """Return int value of internaldate from Gmail API Message response"""
        timestamp = message['internalDate']

        return self._convert_milliseconds_to_datetime(timestamp)

    @staticmethod
    def _convert_milliseconds_to_datetime(milliseconds):
        """Return datetime object from milliseconds"""
        time_in_seconds = int(milliseconds) / 1000.0

        return datetime.fromtimestamp(time_in_seconds)
