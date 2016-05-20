
import requests

from docido_sdk.oauth import OAuthToken
from docido_sdk.toolbox.collections_ext import nameddict


__all__ = [
    'refresh_token',
    'token_info',
]

REFRESH_TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
TOKEN_INFO_URL = 'https://www.googleapis.com/oauth2/v3/tokeninfo'


def refresh_token(token, session=None):
    """Refresh Google OAuth token.

    :param OAuthToken token:
      the token to refresh

    :param requests.Session session:
      Optional `requests` session to use.
    """
    session = session or requests.Session()
    refresh_data = dict(
        refresh_token=token.refresh_token,
        client_id=token.consumer_key,
        client_secret=token.consumer_secret,
        grant_type='refresh_token'
    )
    resp = session.post(REFRESH_TOKEN_URL, data=refresh_data)
    resp_json = resp.json()
    if 'error' in resp_json:
        raise OAuthTokenExpiredError(resp_json['error'])
    consumer_secret = token.consumer_secret
    return OAuthToken(
        access_token=resp_json['access_token'],
        refresh_token=token.refresh_token,
        consumer_key=token.consumer_key,
        consumer_secret=token.consumer_secret
    )


def token_info(token, refresh=True, refresh_cb=None, session=None):
    """
    :param OAuthToken token

    :param bool refresh:
      whether to attempt to refresh the OAuth token if it expired.
      default is `True`.

    :param refresh_cb:
      If specified, a callable object which is given the new token
      in parameter if it has been refreshed.

    :param requests.Session session:
      Optional `requests` session to use.

    :return:
      token information. see
      https://developers.google.com/identity/protocols/OAuth2UserAgent#tokeninfo-validation
      - `scope`: this field is not a space-delimited set of scopes
         but a real Python `set`.
      - `token`: additional field that provides the `OAuthToken`
      - `refreshed`: boolean that will tell if the token has been refreshed
    :rtype: nameddict
    """
    session = session or requests.Session()
    params = dict(access_token=token.access_token)
    resp = session.get(TOKEN_INFO_URL, params=params)
    refreshed = False
    if resp.status_code != 200:
        if refresh:
            token = refresh_token(token, session=session)
            if refresh_cb is not None:
                refreshed = True
                try:
                    refresh_cb(token)
                except Exception:
                    LOGGER.exception('OAuth token refresh callback failed')
    result = resp.json()
    scopes = result.get('scope', '')
    result['scope'] = set(scopes.split(' '))
    result['token'] = token
    result['refreshed'] = refreshed
    return nameddict(result)
