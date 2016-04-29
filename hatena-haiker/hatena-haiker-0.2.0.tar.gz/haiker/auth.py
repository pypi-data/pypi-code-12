#!/usr/bin/env python3
# coding: utf-8

import urllib.parse
import requests
import requests_oauthlib
from . import default, utils


class BasicAuth(requests.auth.HTTPBasicAuth):
    '''Basic Auth handler

    Example:
        >>> auth = haiker.BasicAuth('username', 'password')
        >>> api = haiker.Haiku(auth)
    '''


class OAuth(object):
    '''OAuth handler

    Example 1:
        >>> auth = haiker.OAuth(
        ...     'MyConsumerKey', 'MyConsumerSecret',
        ...     'MyAccessToken', 'MyAccessTokenSecret'
        ... )
        >>> api = haiker.Haiku(auth)

    Example 2:
        >>> auth = haiker.OAuth('MyConsumerKey', 'MyConsumerSecret')
        >>> auth.initiate(['read_public', 'write_public'])
        ('MyRequestToken', 'MyRequestSecret')
        >>> print('GOTO: {url}'.format(url=auth.auth_url()))
        GOTO: https://www.hatena.ne.jp/xxxxx/xxxx?xxx=xxxx
        >>> verifier = 'MyVerifierCode'
        >>> auth.verify(verifier)
        ('MyAccessToken', 'MyAccessTokenSecret')
        >>> api = haiker.Haiku(auth)
    '''
    def __init__(self, consumer_key, consumer_secret=None, oauth_token=None,
                 oauth_token_secret=None, user_agent=default.UA):
        self._keys = {
                'client_key': consumer_key,
                'client_secret': consumer_secret,
                'resource_owner_key': oauth_token,
                'resource_owner_secret': oauth_token_secret,
        }
        self.user_agent = user_agent
        self._auth = self._make_auth(**self._keys)

    def __call__(self, *args, **kwargs):
        return self._auth.__call__(*args, **kwargs)

    def initiate(self, scope, callback_uri='oob', url=default.INITIATE_URL):
        auth = self._make_auth(callback_uri=callback_uri, **self._keys)
        data = {'scope': utils.comma(scope)}
        d = self._post(url, auth, data)
        token = (d['oauth_token'][0], d['oauth_token_secret'][0])
        self._keys['resource_owner_key'] = token[0]
        self._keys['resource_owner_secret'] = token[1]
        self._auth = self._make_auth(**self._keys)
        return token

    def auth_url(self, url=default.AUTH_URL):
        quoted = urllib.parse.quote(self._keys['resource_owner_key'])
        return '{0}?oauth_token={1}'.format(url, quoted)

    def verify(self, oauth_verifier, url=default.TOKEN_URL):
        headers = {'User-Agent': self.user_agent}
        auth = self._make_auth(verifier=oauth_verifier, **self._keys)
        d = self._post(url, auth)
        token = (d['oauth_token'][0], d['oauth_token_secret'][0])
        self._keys['resource_owner_key'] = token[0]
        self._keys['resource_owner_secret'] = token[1]
        self._auth = self._make_auth(**self._keys)
        return token

    def _make_auth(self, **kwargs):
        return requests_oauthlib.OAuth1(**kwargs)

    def _post(self, url, auth, data=None):
        headers = {'User-Agent': self.user_agent}
        res = requests.post(url, auth=auth, headers=headers, data=data)
        utils.check_response(res)
        return urllib.parse.parse_qs(res.text)
