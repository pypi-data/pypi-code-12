import requests
from messenger_sdk.templates import BaseTemplate


class Api:
    def __init__(self, access_token, api_version=2.6):
        self.access_token = access_token
        self.api_version = api_version
        self.endpoint = "https://graph.facebook.com/v{0}/me/messages?access_token={1}".format(
            self.api_version,
            self.access_token
        )

    def send_message(self, message: BaseTemplate):
        return self._send_message_request(message.get_template())

    def _send_message_request(self, payload):
        response = requests.post(self.endpoint, json=payload).json()

        return response
