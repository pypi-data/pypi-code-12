#!/usr/bin/env python3

import urllib.parse
import requests
import requests_oauthlib
from . import error, utils


class BasicAuth(requests.auth.HTTPBasicAuth):
    """Basic Auth handler

    Example:

    >>> auth = haiker.BasicAuth('MyUsername', 'MyPassword')
    >>> api = haiker.Haiker(auth)
    """


class OAuth(object):
    """OAuth handler

    Example 1:

    >>> auth = haiker.OAuth(
    ...     'MyConsumerKey', 'MyConsumerSecret',
    ...     'MyAccessToken', 'MyAccessTokenSecret'
    ... )
    >>> api = haiker.Haiker(auth)

    Example 2:

    >>> auth = haiker.OAuth('MyConsumerKey', 'MyConsumerSecret')
    >>> auth.initiate(['read_public', 'write_public'])
    ('MyRequestToken', 'MyRequestSecret')
    >>> print('GOTO: {url}'.format(url=auth.auth_url()))
    GOTO: https://www.hatena.ne.jp/xxxxx/xxxx?xxx=xxxx
    >>> verifier = 'MyVerifierCode'
    >>> auth.verify(verifier)
    ('MyAccessToken', 'MyAccessTokenSecret')
    >>> api = haiker.Haiker(auth)
    """
    @error.HaikerError.replace
    def __init__(self, consumer_key, consumer_secret=None,
                 oauth_token=None, oauth_token_secret=None, *,
                 user_agent=utils.DEFAULT_USER_AGENT):
        super().__init__()
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

    @error.HaikerError.replace
    def initiate(self, scope, callback_url='oob', *,
                 url='https://www.hatena.com/oauth/initiate'):
        """Fetch a request token pair."""
        self._keys['resource_owner_key'] = None
        self._keys['resource_owner_secret'] = None
        auth = self._make_auth(callback_uri=callback_url, **self._keys)
        return self._receive_token(url, auth, data={'scope': scope})

    @error.HaikerError.replace
    def auth_url(self, *, url='https://www.hatena.ne.jp/oauth/authorize'):
        """Get a URL to authorize.  You can find the verifier code
        to visit the URL.
        """
        key = self._keys['resource_owner_key']
        if key is None:
            clsname = self.__class__.__name__
            msg = 'calling {0}.initiate() before is required'.format(clsname)
            raise RuntimeError(msg)
        quoted = urllib.parse.quote(key)
        return '{url}?oauth_token={query}'.format(url=url, query=quoted)

    @error.HaikerError.replace
    def verify(self, oauth_verifier, *,
               url='https://www.hatena.com/oauth/token'):
        """Fetch an access token pair.  This pair can be two arguments
        in OAuth(): oauth_token and oauth_token_secret.
        """
        auth = self._make_auth(verifier=oauth_verifier, **self._keys)
        return self._receive_token(url, auth)

    def _make_auth(self, **kwargs):
        return requests_oauthlib.OAuth1(**kwargs)

    def _receive_token(self, url, auth, data=None):
        headers = {'User-Agent': self.user_agent}
        res = requests.post(url, auth=auth, headers=headers,
                            data=utils.build_params(data))
        res.raise_for_status()
        d = urllib.parse.parse_qs(res.text)
        token = d['oauth_token'][0]
        token_secret = d['oauth_token_secret'][0]
        self._keys['resource_owner_key'] = token
        self._keys['resource_owner_secret'] = token_secret
        self._auth = self._make_auth(**self._keys)
        return token, token_secret
