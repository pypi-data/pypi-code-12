import base64
import logging
import requests


class FlowdockHandler(logging.Handler):
    """
    An exception log handler that send log entries to a flowdock chat.
    """

    FLOWDOCK_POST_MESSAGE_URL = 'https://api.flowdock.com/flows/{}/{}/messages'

    def __init__(self, api_token=None, organization=None, flow=None):
        logging.Handler.__init__(self)
        self.api_token = api_token
        self.organization = organization
        self.flow = flow

    def emit(self, record):
        data = {
            'event': 'message',
            'content': record.getMessage()
        }

        url = self.FLOWDOCK_POST_MESSAGE_URL.format(self.organization, self.flow)

        requests.post(url, headers=self.get_auth_header(), data=data)

    def get_auth_header(self):
        encoded_api_token = base64.b64encode(self.api_token)
        return {'Authorization': 'Basic {}'.format(encoded_api_token)}
