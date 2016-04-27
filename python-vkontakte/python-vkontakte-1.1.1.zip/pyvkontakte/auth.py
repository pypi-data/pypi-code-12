import logging

import bs4
import requests

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from pyvkontakte.errors import VkontakteAuthError, InvalidCredentials, ParsingError

logger = logging.getLogger(__name__)
__all__ = ['auth']


def _bs_from_response(html):
    """
    Returns BeautifulSoup from given str with html inside.
    :param str html:
    :rtype: bs4.BeautifulSoup
    """
    return bs4.BeautifulSoup(html, "html.parser")


def _build_login_url(client_id, scope):
    base_url = 'http://oauth.vk.com/authorize'
    query = {
        'display': 'mobile',
        'redirect_uri': 'http://oauth.vk.com/blank.html',
        'response_type': 'token',
        'client_id': client_id,
        'scope': scope,
    }
    prepared_request = requests.PreparedRequest()
    prepared_request.prepare('GET', url=base_url, params=query)
    return prepared_request.url


def _process_form(form, session, **kwargs):
    """
    :param bs4.Tag form:
    :param requests.Session session:
    :param dict kwargs:
    :rtype: requests.Response
    """
    action = form['action'] or 'post'
    method = form['method']
    inputs = form.find_all('input', attrs={'type': 'hidden'})
    data = {i['name']: i['value'] for i in inputs if i['value']}
    data.update(kwargs)
    return session.request(method, url=action, data=data)


def _auth_user(login, password, bs, session):
    """
    :param str login:
    :param str password:
    :param bs4.BeautifulSoup bs:
    :param requests.Session session:
    :rtype: requests.Response
    """
    logger.info('Authorizing user: %s', login)
    form = bs.find('form')
    if not form:
        logger.debug(bs)
        raise ParsingError('Form not found on page')
    response = _process_form(form, session, **{'email': login, 'pass': password})
    response.raise_for_status()
    bs = _bs_from_response(response.text)

    warning = bs.find(attrs={'class': 'service_msg_warning'})
    if warning:
        raise InvalidCredentials(warning.text)

    return response


def _give_access(bs, session):
    """
    :param bs4.BeautifulSoup bs:
    :param requests.Session session:
    :rtype: requests.Response
    """
    form = bs.find('form')
    if not form:
        logger.debug(bs)
        raise ParsingError('Form not found on page')
    response = _process_form(form, session)
    response.raise_for_status()

    return response


def auth(login, password, client_id, scope):
    """

    :param str login:
    :param str password:
    :param str|int client_id:
    :param list[str]|str scope:
    :return dict: dict with keys access_token, expires_in, user_id
    """
    scope = scope or []
    if isinstance(scope, str):
        scope = [scope]
    scope = ','.join(scope)

    url = _build_login_url(client_id, scope)
    logger.debug('Login url: %s', url)

    session = requests.Session()

    response = session.get(url)
    response.raise_for_status()

    bs = _bs_from_response(response.text)

    if bs.find('input', attrs={'name': 'pass'}):
        response = _auth_user(login, password, bs, session)

    if '/blank.html' != urlparse(response.url).path:
        bs = _bs_from_response(response.text)
        response = _give_access(bs, session)

    if '/blank.html' == urlparse(response.url).path:
        query = {i[0]: i[1] for i in map(lambda i: i.split("="), urlparse(response.url).fragment.split('&')) if
                 len(i) > 1}
    else:
        raise VkontakteAuthError('Something went wrong. Got url: %s but expected %s', response.url, '/blank.html')
    return query
