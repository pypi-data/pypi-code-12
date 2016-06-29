from demands import JSONServiceClient, HTTPServiceClient


class StageBasedMessagingApiClient(object):
    """
    Client for Stage Based Messaging Service.

    :param str auth_token:

        An access token.

    :param str api_url:
        The full URL of the API.

    """

    def __init__(self, auth_token, api_url, session=None, session_http=None):
        if session is None:
            session = JSONServiceClient(
                url=api_url, headers={'Authorization': 'Token ' + auth_token})

        if session_http is None:
            session_http = HTTPServiceClient(
                url=api_url, headers={'Authorization': 'Token ' + auth_token})
        self.session = session
        self.session_http = session_http

    def get_schedules(self, params=None):
        return self.session.get('/schedule/', params=params)

    def get_messagesets(self, params=None):
        return self.session.get('/messageset/', params=params)

    def get_messages(self, params=None):
        return self.session.get('/message/', params=params)

    def get_message(self, message_id):
        return self.session.get('/message/%s/' % message_id)

    def create_message(self, message):
        return self.session.post('/message/', data=message)

    def delete_message(self, message_id):
        return self.session.delete('/message/%s/' % message_id)

    def delete_binarycontent(self, binarycontent_id):
        return self.session.delete('/binarycontent/%s/' % binarycontent_id)

    def create_binarycontent(self, content):
        return self.session_http.post('/binarycontent/', files=content).json()
