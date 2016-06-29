from demands import JSONServiceClient


class HubApiClient(object):
    """
    Client for Hub Service. a.k.a. registrations/changes

    :param str auth_token:

        An access token.

    :param str api_url:
        The full URL of the API.

    """

    def __init__(self, auth_token, api_url, session=None):
        headers = {'Authorization': 'Token ' + auth_token}
        if session is None:
            session = JSONServiceClient(url=api_url,
                                        headers=headers)
        self.session = session

    def get_registations(self, params=None):
        return self.session.get('/registration/', params=params)

    def get_registation(self, registation_id):
        return self.session.get('/registration/%s/' % registation_id)

    def create_registration(self, registation):
        return self.session.post('/registration/', data=registation)
