import logging

from docido_sdk.crawler import (
    OAuthTokenExpiredError,
    OAuthTokenRefreshRequiredError,
)
from docido_sdk.oauth import OAuthToken
from docido_sdk.toolbox.collections_ext import nameddict
from . http_ext import HTTP_SESSION


__all__ = [
    'refresh_token',
    'token_info',
]

REFRESH_TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
TOKEN_INFO_URL = 'https://www.googleapis.com/oauth2/v3/tokeninfo'
LOGGER = logging.getLogger(__name__)


def refresh_token(token, session=None):
    """Refresh Google OAuth token.

    :param OAuthToken token:
      the token to refresh

    :param requests.Session session:
      Optional `requests` session to use.
    """
    session = session or HTTP_SESSION
    refresh_data = dict(
        refresh_token=token.refresh_token,
        client_id=token.consumer_key,
        client_secret=token.consumer_secret,
        grant_type='refresh_token'
    )
    resp = session.post(REFRESH_TOKEN_URL, data=refresh_data)
    resp_json = resp.json()
    if 'error' in resp_json:
        message = resp_json['error']
        description = resp_json.get('error_description', '')
        if any(description):
            message = u'{}: {}'.format(message, description)
        raise OAuthTokenExpiredError(message)
    return OAuthToken(
        access_token=resp_json['access_token'],
        refresh_token=token.refresh_token,
        consumer_key=token.consumer_key,
        consumer_secret=token.consumer_secret
    )


def __coerce_token_info(info):
    info['email_verified'] = info['email_verified'] == 'true'
    for field in ['exp', 'expires_in']:
        info[field] = int(info[field])
    info['scope'] = set(info.get('scope', '').split(' '))
    return info


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
    session = session or HTTP_SESSION
    params = dict(access_token=token.access_token)
    resp = session.get(TOKEN_INFO_URL, params=params)
    if resp.status_code != 200:
        if refresh:
            token = refresh_token(token, session=session)
            if refresh_cb is not None:
                try:
                    refresh_cb(token)
                except Exception:
                    LOGGER.exception('OAuth token refresh callback failed')
            info = token_info(token, refresh=False, session=session)
            info.update(refreshed=True)
            return info
        raise OAuthTokenRefreshRequiredError()
    info = __coerce_token_info(resp.json())
    info.update(token=token, refreshed=False)
    return nameddict(info)
