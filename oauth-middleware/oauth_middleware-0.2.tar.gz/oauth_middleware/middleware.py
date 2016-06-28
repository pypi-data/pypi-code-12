#!/usr/bin/env python
from __future__ import unicode_literals, absolute_import, division, print_function

import base64
import logging
import re
from copy import deepcopy
from datetime import datetime

from flask import Flask, redirect, url_for, session, request, current_app
from flask_oauthlib.client import OAuth, OAuthException
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.exceptions import Unauthorized, Forbidden, InternalServerError
from six import wraps, raise_from

log = logging.getLogger(__name__)


class ZalandoAuthException(Exception):
    pass


class MissingTokenException(ZalandoAuthException):
    pass


class MissingTokenInfoException(ZalandoAuthException):
    pass

class TokenNotValidException(ZalandoAuthException):
    pass

class TokenIsExpiredException(TokenNotValidException):
    pass


class UnsupportedAuthMethodException(ZalandoAuthException):
    pass


class TokenIsExpired(ZalandoAuthException):
    pass


def get_oauth_token():
    token = None
    if 'Authorization' in request.headers:
        if request.headers['Authorization'].startswith('Bearer'):
            token = request.headers['Authorization']
            token = token.split(' ', 1)[1]
        elif request.headers['Authorization'].startswith('Basic'):
            try:
                auth_header_part = request.headers['Authorization'].split(' ', 1)[1]
                auth_data = base64.b64decode(auth_header_part)
                _, token = auth_data.split(':', 1)
            except Exception as e:
                msg = (
                    "Exception during parsing auth headers: %s",
                    e
                )
                log.exception(msg[0], *msg[1:])
                raise_from(ZalandoAuthException(msg[0] % msg[1:]), e)
        else:
            msg = (
                'Unsupported auth method was specified: %s',
                request.headers['Authorization']
            )
            log.exception(msg[0], *msg[1:])
            raise UnsupportedAuthMethodException(msg[0] % msg[1:])

        if token:
            return token, ''

        # We do not want to fallback to session based auth if Auth header presents
        return None

    token = _get_session_data('token')
    if not token:
        return None
    return token, ''


def is_script_request():
    if 'Authorization' in request.headers:
        return True

    return False


def make_oauth_wsgi(oauth, next_app, config=None):
    app = Flask(__name__, static_folder=None)
    app.config['PROPAGATE_EXCEPTIONS'] = True

    if config:
        app.config.update(config)
    else:
        app.config.from_envvar('OAUTH_SETTINGS')

    app.next_app = next_app
    oauth.init_app(app)
    app.add_url_rule('/login', endpoint=None, view_func=login)
    app.add_url_rule('/logout', endpoint=None, view_func=logout)
    app.add_url_rule('/login/oauth_callback', endpoint=None, view_func=authorized)
    app.add_url_rule(
        '/',
        endpoint=None, view_func=default_handler,
        methods=['GET', 'HEAD', 'POST', 'PUT', 'DELETE'],
    )
    app.add_url_rule(
        '/<path:any>',
        endpoint=None, view_func=default_handler,
        methods=['GET', 'HEAD', 'POST', 'PUT', 'DELETE'],

    )

    auth = get_auth_provider(oauth)
    if not auth._tokengetter:
        auth.tokengetter(get_oauth_token)

    app.wsgi_app = ProxyFix(app.wsgi_app)

    return app


def _set_session_data(key, val):
    session.setdefault('auth_info', {})
    session['auth_info'][key] = val


def _get_session_data(key, default=None):
    session.setdefault('auth_info', {})
    return session['auth_info'].get(key, default)


def _clean_session_data():
    session.pop('auth_info', None)


def request_tokeninfo():
    auth = get_auth_provider()
    tokeninfo = auth.request('tokeninfo')
    log.debug('Got token info: %s:%s', tokeninfo, tokeninfo.data)
    return tokeninfo


def token_info_to_auth_info(token_info):
    from datetime import datetime, timedelta

    auth_info = deepcopy(token_info.data)
    auth_info['expires_at'] = datetime.now() + timedelta(seconds=auth_info.get('expires_in', 31536000))
    if 'uid' in auth_info:
        uid = auth_info['uid']
        auth_info.setdefault('login', uid)
        auth_info.setdefault('email', '{}@zalando.de'.format(uid))
    if 'cn' in auth_info:
        auth_info.setdefault('name', auth_info['cn'])

    return auth_info


def _get_auth_info_from_cache():
    token = get_oauth_token()[0]
    if not token:
        return None

    auth_info = _get_session_data('token_info')

    if not auth_info or not isinstance(auth_info, dict):
        return None
    if auth_info.get('access_token') != token:
        log.debug('Token&tokeninfo mismatch. Token %s, token info: %s', token, auth_info)
        return None
    return auth_info


def get_auth_info(cache=True):
    if not cache or not _get_auth_info_from_cache():
        token_info = request_tokeninfo()
        if token_info.status == 200:
            _set_session_data('token_info', token_info_to_auth_info(token_info))
        elif token_info.status == 400:
            # Probably token not valid
            msg = "Can't get info for token. Rerequest? %s:%s", token_info, token_info.data
            log.warn(msg[0], *msg[1:])
            raise TokenNotValidException(msg)
        else:
            msg = "Error while getting token info %s:%s", token_info, token_info.data
            log.warn(msg[0], *msg[1:])
            raise MissingTokenInfoException(msg[0] % msg[1:])

    return _get_auth_info_from_cache()


def check_auth():
    """
    Check are we authorised
    :return: True if we authorised
        False if no auth provided
        exception if provided auth is wrong
    """
    if get_oauth_token():
        auth_info = get_auth_info()
        if not auth_info:
            raise MissingTokenInfoException("Could not get token info")
        if datetime.now() >= auth_info['expires_at']:
            msg = (
                'Token is expired. Now %s but valid until %s',
                datetime.now(), auth_info['expires_at']
            )

            log.warn(
                msg[0], *msg[1:]
            )
            raise TokenIsExpired(msg[0] % msg[1:])
    else:
        raise MissingTokenException()


def get_auth_provider(oauth=None):
    if not oauth:
        from flask import current_app
        oauth = current_app.extensions[OAuth.state_key]
    if len(oauth.remote_apps) != 1:
        raise ZalandoAuthException('Multiple or none oauth providers not supported now')

    return list(oauth.remote_apps.values())[0]  # to be 2/3 compatible


def auth_required(view=None, **auth_args):
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            skip_auth = False
            if auth_args['skip_on']:
                skip_auth = auth_args['skip_on']()

            try:
                if not skip_auth:
                    check_auth()  # this will raise exception if auth needed
                return view(*args, **kwargs)

            except (MissingTokenException, TokenNotValidException, TokenIsExpired) as e:
                log.debug("Can't' authorize user")
                if is_script_request():
                    raise Unauthorized('Problem on auth step {}'.format(e))
                else:
                    log.debug('Initiating web-browser auth flow. Because %s', e)
                    return redirect(url_for('login'))
            except ZalandoAuthException as e:
                log.exception('Exception during authorization: %s', e)
                return InternalServerError('Exception occurred during authorization process. Check server logs')

        return wrapper

    # simple decorator
    if view and callable(view) and not auth_args:
        return decorator(view)
    else:
        return decorator


def _skip_auth_on_pattern():
    from flask import current_app, request
    for url_to_skip in current_app.config['SKIP_AUTH_FOR']:
        if re.search(url_to_skip, request.path):
            return True
    return False


@auth_required(skip_on=_skip_auth_on_pattern)
def default_handler(*args, **kwargs):
    log.info('Calling to next app')
    return PassingResponse(current_app.next_app)


def login():
    auth_provider = get_auth_provider()
    return auth_provider.authorize(callback=url_for('authorized', _external=True))


def logout():
    _clean_session_data()
    return redirect(url_for('default_handler'))


def get_user_info():
    return get_auth_info()


class PassingResponse:
    def __init__(self, nxt):
        self._nxt = nxt

    def __call__(self, environ, start_response):
        token = _get_session_data('token', None)
        token_info = _get_session_data('token_info', None)

        environ['OAUTH_TOKEN'] = token
        environ['OAUTH_TOKEN_INFO'] = token_info

        return self._nxt(environ, start_response)


def authorized():
    auth_provider = get_auth_provider()

    try:
        resp = auth_provider.authorized_response()
        if resp is None:
            raise Forbidden('Access denied: reason=%s error=%s' % (
                request.args['error'],
                request.args['error_description']
            ))
        if not isinstance(resp, dict):
            raise Forbidden('Invalid auth response %s' % (resp,))
        log.info("Auth success: %s", resp)

        _set_session_data('token', resp['access_token'])
        _set_session_data('token_info', get_auth_info())

        return redirect(current_app.config['SUCCESS_LOGIN_PATH'])
    except OAuthException as e:
        msg = 'OAuth failed %s:%s', e, e.data
        log.exception(*msg)
        raise InternalServerError(msg[0] % msg[1:])


if __name__ == '__main__':
    from zalando_oauth import make_zalando_oauth

    # development mode: run Flask dev server
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(logging.DEBUG)

    test_app = Flask('lalala')


    @test_app.route('/')
    def idx():
        return "Index: {}".format(test_app.url_map)


    @test_app.route('/lalala')
    def lalala():
        return 'Crazy cats!'


    application = make_oauth_wsgi(make_zalando_oauth(), test_app)
    application.run(
        ssl_context=('./server.pem', './server.key'),
        debug=True,
    )
