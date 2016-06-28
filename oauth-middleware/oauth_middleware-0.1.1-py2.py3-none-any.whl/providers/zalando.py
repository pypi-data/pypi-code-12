from __future__ import division, unicode_literals, print_function, absolute_import

import os
import logging
import json
from flask_oauthlib.client import OAuthRemoteApp, OAuth

log = logging.getLogger(__name__)


class OAuthRemoteAppWithRefresh(OAuthRemoteApp):
    """
    Same as flask_oauthlib.client.OAuthRemoteApp, but always loads client credentials from file.

    Based on https://github.com/zalando-stups/oauth2-proxy
    """

    def __init__(self, oauth, name, credentials_dir=None, **kwargs):
        # constructor expects some values, so make it happy..
        kwargs['consumer_key'] = 'not-needed-here'
        kwargs['consumer_secret'] = 'not-needed-here'

        self._credentials_dir = credentials_dir
        OAuthRemoteApp.__init__(self, oauth, name, **kwargs)

    def refresh_credentials(self):
        credentials_dir = self._get_property('credentials_dir', './')

        with open(os.path.join(credentials_dir, 'client.json')) as fd:
            client_credentials = json.load(fd)
        self._consumer_key = client_credentials['client_id']
        self._consumer_secret = client_credentials['client_secret']

    @property
    def consumer_key(self):
        self.refresh_credentials()
        return self._consumer_key

    @property
    def consumer_secret(self):
        self.refresh_credentials()
        return self._consumer_secret


def make_zalando_oauth():
    oauth = OAuth()

    auth = OAuthRemoteAppWithRefresh(
        oauth,
        'zalando_oauth',
        app_key='ZALANDO_OAUTH',
    )
    oauth.remote_apps['zalando_oauth'] = auth

    return oauth
