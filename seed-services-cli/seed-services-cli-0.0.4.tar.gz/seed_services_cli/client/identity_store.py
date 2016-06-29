from demands import JSONServiceClient


class IdentityStoreApiClient(object):
    """
    Client for Identity Store Service.

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

    def get_identities(self, params=None):
        return self.session.get('/identities/', params=params)

    def get_identity(self, identity_id):
        return self.session.get('/identities/%s/' % identity_id)

    def create_identity(self, identity):
        return self.session.post('/identities/', data=identity)

    def get_identity_by_address(self, address_type, address_value):
        params = {"details__addresses__%s" % address_type: address_value}
        return self.session.get('/identities/search/', params=params)
