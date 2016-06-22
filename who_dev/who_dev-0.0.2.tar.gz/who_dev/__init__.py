"""
User source for development purposes on systems using repoze.who v2 API
"""

import json
import logging

from repoze.who.interfaces import IAuthenticator, IMetadataProvider
from zope.interface import implementer


log = logging.getLogger('repoze.who').getChild('who_dev')

_DATA = None


def _initdb(data):
    global _DATA

    if data is None:
        return

    _DATA = json.loads(data)


@implementer(IAuthenticator)
class JSONAuthenticatorPlugin(object):
    """
    Authenticates using the userid as a key
    """

    def __init__(self, data=None):
        """
        Parameters:
        data -- (optional) JSON data (will initialize singleton user table)
        """
        _initdb(data)

    # IAuthenticator
    def authenticate(self, environ, identity):
        try:
            login = identity['login']
            password = identity['password']
        except KeyError:
            log.error('Missing login/password keys in identity')
            return

        try:
            user = _DATA[login]
        except KeyError:
            log.debug('Not found: "%s" ' % login)
            return
        if user['password'] == password:
            log.debug('Authenticated: "%s"' % login)
            return login
        else:
            log.debug('Incorrect password for user: "%s"')


@implementer(IMetadataProvider)
class JSONPropertiesPlugin(object):
    """
    Loads attributes of the authenticated user.
    """

    def __init__(self, data=None, source_key=None, target_key=None):
        """
        Parameters:
        source_key -- (required) Key in user table to extract
        target_key -- (optional) Key in identity to use for data
        data -- (optional) JSON data (will initialize singleton user table)
        """
        _initdb(data)

        if source_key is None:
            log.warn('"source_key" is required')

        self.source_key = source_key
        self.target_key = target_key if target_key else source_key

    # IMetadataProvider
    def add_metadata(self, environ, identity):

        if _DATA is None:
            log.warn('User table was not initilized')
            return

        userid = identity.get('repoze.who.userid')
        user = _DATA[userid]
        source_value = user.get(self.source_key)
        identity[self.target_key] = source_value
