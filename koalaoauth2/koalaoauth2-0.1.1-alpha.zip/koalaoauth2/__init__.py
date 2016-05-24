# -*- coding: utf-8 -*-
"""
    koalacoreoauth2.__init__.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Oauth2 Provider module. Exposes methods required for oauth2 auth flows.
    
    :copyright: (c) 2015 Lighthouse
    :license: LGPL
"""

import koalacore
from blinker import signal
import os
from google.appengine.ext import ndb
from datetime import datetime, timedelta
import logging
from urlparse import urlparse, parse_qsl
from urllib import unquote_plus
import binascii
import base64
from oauthlib.common import generate_client_id as oauthlib_generate_client_id
from oauthlib.common import UNICODE_ASCII_CHARACTER_SET
from oauthlib.oauth2 import RequestValidator, WebApplicationServer, BackendApplicationServer, OAuth2Error, FatalClientError, AccessDeniedError

__author__ = 'Matt Badger'

ALLOWED_REDIRECT_URI_SCHEMES = ['http', 'https']
ACCESS_TOKEN_EXPIRE_SECONDS = 36000
AUTHORIZATION_CODE_EXPIRE_SECONDS = 60
_SCOPES = ['user.profile']
CLIENT_ID_GENERATOR_LENGTH = 40
CLIENT_SECRET_GENERATOR_LENGTH = 128

CLIENT_CONFIDENTIAL = 'confidential'
CLIENT_PUBLIC = 'public'
CLIENT_TYPES = (
    (CLIENT_CONFIDENTIAL, 'Confidential'),
    (CLIENT_PUBLIC, 'Public'),
)
CLIENT_TYPES_LIST = [
    CLIENT_CONFIDENTIAL,
    CLIENT_PUBLIC,
]
# This mapping setup was copied from flask/django implementations. It doesn't appear to server any purpose except making
# the code more complicated than it needs to be.
GRANT_AUTHORIZATION_CODE = 'authorization-code'
GRANT_IMPLICIT = 'implicit'
GRANT_PASSWORD = 'password'
GRANT_CLIENT_CREDENTIALS = 'client-credentials'
GRANT_TYPES = (
    (GRANT_AUTHORIZATION_CODE, 'Authorization code'),
    (GRANT_IMPLICIT, 'Implicit'),
    (GRANT_PASSWORD, 'Resource owner password-based'),
    (GRANT_CLIENT_CREDENTIALS, 'Client credentials'),
)
GRANT_TYPES_LIST = [
    GRANT_AUTHORIZATION_CODE,
    GRANT_IMPLICIT,
    GRANT_PASSWORD,
    GRANT_CLIENT_CREDENTIALS,
]
GRANT_TYPE_MAPPING = {
    'authorization_code': (GRANT_AUTHORIZATION_CODE,),
    'password': (GRANT_PASSWORD,),
    'client_credentials': (GRANT_CLIENT_CREDENTIALS,),
    'refresh_token': (GRANT_AUTHORIZATION_CODE, GRANT_PASSWORD, GRANT_CLIENT_CREDENTIALS)
}


def validate_uris(value):
    """
    This validator ensures that `value` contains valid blank-separated URIs"
    """
    v = koalacore.ConditionalURIValidator(allowed_schemes=ALLOWED_REDIRECT_URI_SCHEMES, allow_fragments=False)
    for uri in value.split():
        v(uri)


def ndb_validate_redirect_uris(property, value):
    return validate_uris(value=value)


def generate_client_id(length=None):
    if not length:
        length = CLIENT_ID_GENERATOR_LENGTH
    return oauthlib_generate_client_id(length=length, chars=UNICODE_ASCII_CHARACTER_SET)


def generate_client_secret():
    return oauthlib_generate_client_id(length=CLIENT_SECRET_GENERATOR_LENGTH, chars=UNICODE_ASCII_CHARACTER_SET)

# Begin Model definitions


class Client(koalacore.Resource):
    guid = koalacore.ResourceProperty(title=u'Related UID')
    redirect_uris = koalacore.ResourceProperty(title=u'Redirect URIs')
    client_type = koalacore.ResourceProperty(title=u'Client Type')
    authorization_grant_type = koalacore.ResourceProperty(title=u'Grant Type')
    client_id = koalacore.ResourceProperty(title=u'Client UID', unique=True)
    client_secret = koalacore.ResourceProperty(title=u'Client Secret')
    client_name = koalacore.ResourceProperty(title=u'Client Name')
    skip_authorization = koalacore.ResourceProperty(title=u'Skip Authorization', default=False)

    def __init__(self, **kwargs):
        if not kwargs.get('client_secret', None):
            kwargs['client_secret'] = generate_client_secret()

        super(Client, self).__init__(**kwargs)

    def __repr__(self):
        return u'Oauth2 Client ({}); ID: [{}]'.format(self.client_name or 'anon', self.client_id or 'n/a')

    @property
    def default_redirect_uri(self):
        """
        Returns the default redirect_uri extracting the first item from
        the :attr:`redirect_uris` string
        """
        if self.redirect_uris:
            return self.redirect_uris.split().pop(0)

        assert False, "If you are using implicit, authorization_code or all-in-one grant_type, you must define " \
                      "redirect_uris field for the client"

    def redirect_uri_allowed(self, uri):
        """
        Checks if given url is one of the items in :attr:`redirect_uris` string
        :param uri: Url to check
        """
        for allowed_uri in self.redirect_uris.split():
            parsed_allowed_uri = urlparse(allowed_uri)
            parsed_uri = urlparse(uri)

            if (parsed_allowed_uri.scheme == parsed_uri.scheme and
                    parsed_allowed_uri.netloc == parsed_uri.netloc and
                    parsed_allowed_uri.path == parsed_uri.path):

                aqs_set = set(parse_qsl(parsed_allowed_uri.query))
                uqs_set = set(parse_qsl(parsed_uri.query))

                if aqs_set.issubset(uqs_set):
                    return True

        return False

    def clean(self):
        if not self.redirect_uris and self.authorization_grant_type in (NDBClientModel.GRANT_AUTHORIZATION_CODE, NDBClientModel.GRANT_IMPLICIT):
            error = 'Redirect_uris could not be empty with {0} grant_type'
            raise ValueError(error.format(self.authorization_grant_type))

    def to_search_doc(self):
        return [
            koalacore.GAESearchInterface.text_field(name='fuzzy_client_name',
                                                value=koalacore.generate_autocomplete_tokens(original_string=self.client_name)),
            koalacore.GAESearchInterface.date_field(name='created', value=self.created),
            koalacore.GAESearchInterface.date_field(name='updated', value=self.updated),
            koalacore.GAESearchInterface.atom_field(name='guid', value=self.guid),
            koalacore.GAESearchInterface.atom_field(name='redirect_uris', value=self.redirect_uris),
            koalacore.GAESearchInterface.atom_field(name='client_type', value=self.client_type),
            koalacore.GAESearchInterface.atom_field(name='authorization_grant_type', value=self.authorization_grant_type),
            koalacore.GAESearchInterface.atom_field(name='client_id', value=self.client_id),
            koalacore.GAESearchInterface.atom_field(name='client_secret', value=self.client_secret),
            koalacore.GAESearchInterface.atom_field(name='client_name', value=self.client_name),
            koalacore.GAESearchInterface.atom_field(name='skip_authorization',
                                                value='Y' if self.skip_authorization else 'N'),
        ]


class NDBClientModel(koalacore.NDBResource):
    """
    An Application instance represents a Client on the Authorization server.
    Usually an Application is created manually by client's developers after
    logging in on an Authorization Server.

    `client_id` is actually the ndb.Key.id.

    This allows for fast retrieval from NDB without a query, but it does break the interface somewhat. See
    ClientNDBInterface for more information about the modifications made.

    Fields:
    * :attr:`guid` ref to a user/unique entity (implementation of user/entity is not relevant here)
    * :attr:`redirect_uris` The list of allowed redirect uri. The string
                            consists of valid URLs separated by space
    * :attr:`client_type` Client type as described in :rfc:`2.1`
    * :attr:`authorization_grant_type` Authorization flows available to the
                                       Application
    * :attr:`client_id` Client identifier issued to the client during the registration process
                        as described in :rfc:`2.2`
    * :attr:`client_secret` Confidential secret issued to the client during
                            the registration process as described in :rfc:`2.2`
    * :attr:`client_name` Friendly name for the Application
    """
    guid = ndb.StringProperty('cguid', indexed=False)
    redirect_uris = ndb.StringProperty('cru', indexed=False, validator=ndb_validate_redirect_uris)
    client_type = ndb.StringProperty('ct', indexed=False, choices=CLIENT_TYPES_LIST)
    authorization_grant_type = ndb.StringProperty('cagt', indexed=False, choices=GRANT_TYPES_LIST)
    client_id = ndb.StringProperty('cid', indexed=False)
    client_secret = ndb.StringProperty('cs', indexed=False)
    client_name = ndb.StringProperty('cn', indexed=False)
    skip_authorization = ndb.BooleanProperty('csa', default=False, indexed=False)


class ClientNDBInterface(koalacore.NDBEventedInterface):
    _datastore_model = NDBClientModel
    _resource_object = Client


class ClientSearchInterface(koalacore.GAESearchInterface):
    _index_name = 'clients'
    _resource_object = Client


class Clients(koalacore.BaseAPI):
    _api_name = 'clients'
    _api_model = Client
    _datastore_interface = ClientNDBInterface
    _search_interface = ClientSearchInterface

    @classmethod
    def _convert_client_id_to_datastore_key(cls, client_id):
        # The id passed to this function if actually client_id, which is the ndb.Key.id
        # We therefore need to convert it to a proper ndb key before passing it on to the get function
        return cls._datastore_interface.build_resource_uid(desired_id=client_id)

    @classmethod
    def new(cls, **kwargs):
        # Unfortunately we have to do this here so that the uid can be set. The uid relies on knowing the implementation
        # of the datastore and thus does not belong in the resource object definition.
        if not kwargs.get('client_id', None):
            kwargs['client_id'] = generate_client_id()

        kwargs['uid'] = cls._convert_client_id_to_datastore_key(client_id=kwargs['client_id'])

        return super(Clients, cls).new(**kwargs)

    @classmethod
    def insert(cls, resource_object, **kwargs):
        resource_uid = super(Clients, cls).insert(resource_object=resource_object, **kwargs)
        return cls._datastore_interface._convert_string_to_ndb_key(datastore_key=resource_uid).id()

    @classmethod
    def get(cls, resource_uid, **kwargs):
        resource_uid = cls._convert_client_id_to_datastore_key(client_id=resource_uid)
        resource_object = super(Clients, cls).get(resource_uid=resource_uid, **kwargs)
        # TODO: This is a really nasty way to convert the UID - it will lead to bugs down the road; fix
        try:
            resource_object._values['uid'] = resource_object.client_id
        except AttributeError:
            pass
        return resource_object

    @classmethod
    def update(cls, resource_object, **kwargs):
        resource_object._values['uid'] = cls._convert_client_id_to_datastore_key(client_id=resource_object.client_id)
        resource_uid = super(Clients, cls).update(resource_object=resource_object, **kwargs)
        return cls._datastore_interface._convert_string_to_ndb_key(datastore_key=resource_uid).id()

    @classmethod
    def patch(cls, resource_uid, delta_update, **kwargs):
        resource_uid = cls._convert_client_id_to_datastore_key(client_id=resource_uid)
        return super(Clients, cls).patch(resource_uid=resource_uid, delta_update=delta_update, **kwargs)

    @classmethod
    def delete(cls, resource_uid, **kwargs):
        resource_uid = cls._convert_client_id_to_datastore_key(client_id=resource_uid)
        return super(Clients, cls).delete(resource_uid=resource_uid, **kwargs)

    @classmethod
    def _update_search_index(cls, resource_uid, **kwargs):
        # Update method uses get to load the client. Get uses the client_id and converts it to a key. We need to do that
        # convert the datastore key passed from update back into a client_id so that it can be fetched by the search
        # index update below.
        client_id = cls._datastore_interface._convert_string_to_ndb_key(datastore_key=resource_uid).id()
        super(Clients, cls)._update_search_index(resource_uid=client_id, **kwargs)

    @classmethod
    def _delete_search_index(cls, resource_uid, **kwargs):
        # Delete method needs the NDB key in order to delete the search index, so we must manually convert it here
        client_id = cls._datastore_interface._convert_string_to_ndb_key(datastore_key=resource_uid).id()
        super(Clients, cls)._delete_search_index(resource_uid=client_id, **kwargs)


class AccessToken(koalacore.Resource):
    guid = koalacore.ResourceProperty(title=u'Related UID')
    token = koalacore.ResourceProperty(title=u'Token')
    client_id = koalacore.ResourceProperty(title=u'Client UID')
    expires = koalacore.ResourceProperty(title=u'Expiry Date')
    scope = koalacore.ResourceProperty(title=u'Scopes')

    def __repr__(self):
        return u'Oauth2 Access Token \'{}\' for GUID \'{}\''.format(self.token, self.guid)

    def is_valid(self, scopes=None):
        """
        Checks if the access token is valid.
        :param scopes: An iterable containing the scopes to check or None
        """
        return not self.is_expired() and self.allow_scopes(scopes)

    def is_expired(self):
        """
        Check token expiration with timezone awareness
        """
        return datetime.utcnow() >= self.expires

    def allow_scopes(self, scopes):
        """
        Check if the token allows the provided scopes
        :param scopes: An iterable containing the scopes to check
        """
        if not scopes:
            return True

        provided_scopes = set(self.scope.split())
        resource_scopes = set(scopes)

        return resource_scopes.issubset(provided_scopes)

    def to_search_doc(self):
        return [
            koalacore.GAESearchInterface.date_field(name='created', value=self.created),
            koalacore.GAESearchInterface.date_field(name='updated', value=self.updated),
            koalacore.GAESearchInterface.atom_field(name='guid', value=self.guid),
            koalacore.GAESearchInterface.atom_field(name='token', value=self.token),
            koalacore.GAESearchInterface.atom_field(name='client_id', value=self.client_id),
            koalacore.GAESearchInterface.date_field(name='expires', value=self.expires),
            koalacore.GAESearchInterface.text_field(name='scope', value=self.scope),
        ]


class NDBAccessTokenModel(koalacore.NDBResource):
    """
    An AccessToken instance represents the actual access token to
    access user's resources, as in :rfc:`5`.
    Fields:
    * :attr:`guid` ref to a user/unique entity (implementation of user/entity is not relevant here)
    * :attr:`token` Access token
    * :attr:`client` Client entity
    * :attr:`expires` Date and time of token expiration, in DateTime format
    * :attr:`scope` Allowed scopes
    """
    guid = ndb.StringProperty('atguid', indexed=False)
    token = ndb.StringProperty('att', indexed=False)
    client_id = ndb.StringProperty('atcid', indexed=False)
    expires = ndb.DateTimeProperty('ate', indexed=False)
    scope = ndb.TextProperty('gs')


class AccessTokenNDBInterface(koalacore.NDBEventedInterface):
    _datastore_model = NDBAccessTokenModel
    _resource_object = AccessToken


class AccessTokenSearchInterface(koalacore.GAESearchInterface):
    _index_name = 'access_tokens'
    _resource_object = AccessToken


class AccessTokens(koalacore.BaseAPI):
    _api_name = 'access_tokens'
    _api_model = AccessToken
    _datastore_interface = AccessTokenNDBInterface
    _search_interface = AccessTokenSearchInterface

    @classmethod
    def _convert_token_to_datastore_key(cls, token):
        return cls._datastore_interface.build_resource_uid(desired_id=token)

    @classmethod
    def new(cls, **kwargs):
        kwargs['uid'] = cls._convert_token_to_datastore_key(token=kwargs['token'])

        return super(AccessTokens, cls).new(**kwargs)

    @classmethod
    def get(cls, resource_uid, **kwargs):
        resource_uid = cls._convert_token_to_datastore_key(token=resource_uid)
        resource_object = super(AccessTokens, cls).get(resource_uid=resource_uid, **kwargs)
        try:
            resource_object._values['uid'] = resource_object.token
        except AttributeError:
            pass
        return resource_object

    @classmethod
    def update(cls, resource_object, **kwargs):
        raise NotImplementedError

    @classmethod
    def delete(cls, resource_uid, **kwargs):
        resource_uid = cls._convert_token_to_datastore_key(token=resource_uid)
        return super(AccessTokens, cls).delete(resource_uid=resource_uid, **kwargs)

    @classmethod
    def _update_search_index(cls, resource_uid, **kwargs):
        # Update method uses get to load the client. Get uses the client_id and converts it to a key. We need to do that
        # convert the datastore key passed from update back into a client_id so that it can be fetched by the search
        # index update below.
        client_id = cls._datastore_interface._convert_string_to_ndb_key(datastore_key=resource_uid).id()
        super(AccessTokens, cls)._update_search_index(resource_uid=client_id, **kwargs)

    @classmethod
    def _delete_search_index(cls, resource_uid, **kwargs):
        # Delete method needs the NDB key in order to delete the search index, so we must manually convert it here
        client_id = cls._datastore_interface._convert_string_to_ndb_key(datastore_key=resource_uid).id()
        super(AccessTokens, cls)._delete_search_index(resource_uid=client_id, **kwargs)


class RefreshToken(koalacore.Resource):
    guid = koalacore.ResourceProperty(title=u'Related UID')
    token = koalacore.ResourceProperty(title=u'Token')
    client_id = koalacore.ResourceProperty(title=u'Client UID')
    access_token = koalacore.ResourceProperty(title=u'Access Token')

    def __repr__(self):
        return u'Oauth2 Access Token \'{}\' for GUID \'{}\''.format(self.token, self.guid)

    def to_search_doc(self):
        return [
            koalacore.GAESearchInterface.date_field(name='created', value=self.created),
            koalacore.GAESearchInterface.date_field(name='updated', value=self.updated),
            koalacore.GAESearchInterface.atom_field(name='guid', value=self.guid),
            koalacore.GAESearchInterface.atom_field(name='token', value=self.token),
            koalacore.GAESearchInterface.atom_field(name='client_id', value=self.client_id),
            koalacore.GAESearchInterface.atom_field(name='access_token', value=self.access_token),
        ]


class NDBRefreshTokenModel(koalacore.NDBResource):
    """
    A RefreshToken instance represents a token that can be swapped for a new access token when it expires.
    Fields:
    * :attr:`guid` ref to a user/unique entity (implementation of user/entity is not relevant here)
    * :attr:`token` Token value
    * :attr:`application` Application instance
    * :attr:`access_token` AccessToken this refresh token is bounded to
    """
    guid = ndb.StringProperty('rtguid', indexed=False)
    token = ndb.StringProperty('rtt', indexed=True)
    client_id = ndb.StringProperty('rtcid', indexed=False)
    access_token = ndb.StringProperty('rtat', indexed=False)


class RefreshTokenNDBInterface(koalacore.NDBEventedInterface):
    _datastore_model = NDBRefreshTokenModel
    _resource_object = RefreshToken


class RefreshTokenSearchInterface(koalacore.GAESearchInterface):
    _index_name = 'refresh_tokens'
    _resource_object = RefreshToken


class RefreshTokens(koalacore.BaseAPI):
    _api_name = 'refresh_tokens'
    _api_model = RefreshToken
    _datastore_interface = RefreshTokenNDBInterface
    _search_interface = RefreshTokenSearchInterface

    @classmethod
    def _convert_token_to_datastore_key(cls, token):
        return cls._datastore_interface.build_resource_uid(desired_id=token)

    @classmethod
    def new(cls, **kwargs):
        kwargs['uid'] = cls._convert_token_to_datastore_key(token=kwargs['token'])

        return super(RefreshTokens, cls).new(**kwargs)

    @classmethod
    def get(cls, resource_uid, **kwargs):
        resource_uid = cls._convert_token_to_datastore_key(token=resource_uid)
        resource_object = super(RefreshTokens, cls).get(resource_uid=resource_uid, **kwargs)
        try:
            resource_object._values['uid'] = resource_object.token
        except AttributeError:
            pass
        return resource_object

    @classmethod
    def update(cls, resource_object, **kwargs):
        raise NotImplementedError

    @classmethod
    def delete(cls, resource_uid, **kwargs):
        resource_uid = cls._convert_token_to_datastore_key(token=resource_uid)
        return super(RefreshTokens, cls).delete(resource_uid=resource_uid, **kwargs)

    @classmethod
    def _update_search_index(cls, resource_uid, **kwargs):
        # Update method uses get to load the client. Get uses the client_id and converts it to a key. We need to do that
        # convert the datastore key passed from update back into a client_id so that it can be fetched by the search
        # index update below.
        client_id = cls._datastore_interface._convert_string_to_ndb_key(datastore_key=resource_uid).id()
        super(RefreshTokens, cls)._update_search_index(resource_uid=client_id, **kwargs)

    @classmethod
    def _delete_search_index(cls, resource_uid, **kwargs):
        # Delete method needs the NDB key in order to delete the search index, so we must manually convert it here
        client_id = cls._datastore_interface._convert_string_to_ndb_key(datastore_key=resource_uid).id()
        super(RefreshTokens, cls)._delete_search_index(resource_uid=client_id, **kwargs)


class Grant(koalacore.Resource):
    guid = koalacore.ResourceProperty(title=u'Related UID')
    code = koalacore.ResourceProperty(title=u'Authorization Code')
    client_id = koalacore.ResourceProperty(title=u'Client UID')
    expires = koalacore.ResourceProperty(title=u'Expiry Date')
    redirect_uri = koalacore.ResourceProperty(title=u'Redirect URI')
    scope = koalacore.ResourceProperty(title=u'Scopes')

    def __repr__(self):
        return u'Oauth2 Authorization Code \'{}\' for GUID \'{}\''.format(self.code, self.guid)

    def is_expired(self):
        """
        Check token expiration with timezone awareness
        """
        return datetime.utcnow() >= self.expires

    def redirect_uri_allowed(self, uri):
        return uri == self.redirect_uri

    def to_search_doc(self):
        return [
            koalacore.GAESearchInterface.date_field(name='created', value=self.created),
            koalacore.GAESearchInterface.date_field(name='updated', value=self.updated),
            koalacore.GAESearchInterface.atom_field(name='guid', value=self.guid),
            koalacore.GAESearchInterface.atom_field(name='code', value=self.code),
            koalacore.GAESearchInterface.atom_field(name='client_id', value=self.client_id),
            koalacore.GAESearchInterface.date_field(name='expires', value=self.expires),
            koalacore.GAESearchInterface.atom_field(name='redirect_uri', value=self.redirect_uri),
            koalacore.GAESearchInterface.text_field(name='scope', value=self.scope),
        ]


class NDBGrantModel(koalacore.NDBResource):
    """
    A Grant instance represents a token with a short lifetime that can
    be swapped for an access token, as described in :rfc:`4.1.2`
    Fields:
    * :attr:`guid` ref to a user/unique entity (implementation of user/entity is not relevant here)
    * :attr:`code` The authorization code generated by the authorization server
    * :attr:`client` Client entity this grant was asked for
    * :attr:`expires` Expire time in seconds, defaults to
                      :data:`settings.AUTHORIZATION_CODE_EXPIRE_SECONDS`
    * :attr:`redirect_uri` Self explained
    * :attr:`scope` Required scopes, optional
    """
    guid = ndb.StringProperty('gguid', indexed=False)
    code = ndb.StringProperty('gc', indexed=True)  # code comes from oauthlib
    client_id = ndb.StringProperty('gcid', indexed=True)
    expires = ndb.DateTimeProperty('ge', indexed=False)
    redirect_uri = ndb.StringProperty('gru', indexed=False)
    scope = ndb.TextProperty('gs')

    def __str__(self):
        return self.code


class GrantNDBInterface(koalacore.NDBEventedInterface):
    _datastore_model = NDBGrantModel
    _resource_object = Grant


class GrantSearchInterface(koalacore.GAESearchInterface):
    _index_name = 'grants'
    _resource_object = Grant


class Grants(koalacore.BaseAPI):
    _api_name = 'grants'
    _api_model = Grant
    _datastore_interface = GrantNDBInterface
    _search_interface = GrantSearchInterface

    @classmethod
    def _convert_client_id_to_datastore_key(cls, code, client_id):
        return cls._datastore_interface.build_resource_uid(desired_id=u'{}_{}'.format(code, client_id))

    @classmethod
    def new(cls, **kwargs):
        kwargs['uid'] = cls._convert_client_id_to_datastore_key(code=kwargs['code'], client_id=kwargs['client_id'])

        return super(Grants, cls).new(**kwargs)

# End Model definitions


# TODO: potentially convert this to be a static class; use class methods. It should not use any kind of state
class OAuth2RequestValidator(RequestValidator):
    _client_interface = Clients
    _grant_interface = Grants
    _access_token_interface = AccessTokens
    _refresh_token_interface = RefreshTokens

    @staticmethod
    def _extract_basic_auth(request):
        """
        Return authentication string if request contains basic auth credentials, else return None
        """
        auth = None
        try:
            auth = request.headers['Authorization']
        except KeyError:
            try:
                auth = request.headers['authorization']
            except KeyError:
                try:
                    auth = request.headers['HTTP_AUTHORIZATION']
                except KeyError:
                    pass

        if not auth:
            return None

        splitted = auth.split(' ', 1)
        if len(splitted) != 2:
            return None
        auth_type, auth_string = splitted

        if auth_type != "Basic":
            return None

        return auth_string

    def _authenticate_basic_auth(self, request):
        """
        Authenticates with HTTP Basic Auth.

        Note: as stated in rfc:`2.3.1`, client_id and client_secret must be encoded with
        "application/x-www-form-urlencoded" encoding algorithm.
        """
        auth_string = self._extract_basic_auth(request)
        if not auth_string:
            return False

        try:
            encoding = request.encoding
        except AttributeError:
            encoding = 'utf-8'

        try:
            b64_decoded = base64.b64decode(auth_string)
        except (TypeError, binascii.Error):
            logging.debug("Failed basic auth: %s can't be decoded as base64", auth_string)
            return False

        try:
            auth_string_decoded = b64_decoded.decode(encoding)
        except UnicodeDecodeError:
            logging.debug("Failed basic auth: %s can't be decoded as unicode by %s", auth_string, encoding)
            return False

        client_id, client_secret = map(unquote_plus, auth_string_decoded.split(':', 1))

        if self._load_client(client_id, request) is None:
            logging.debug("Failed basic auth: Application %s does not exist" % client_id)
            return False
        elif request.client.client_secret != client_secret:
            logging.debug("Failed basic auth: wrong client secret %s" % client_secret)
            return False
        else:
            return True

    def _authenticate_request_body(self, request):
        """
        Try to authenticate the client using client_id and client_secret parameters
        included in body.

        Remember that this method is NOT RECOMMENDED and SHOULD be limited to clients unable to
        directly utilize the HTTP Basic authentication scheme. See rfc:`2.3.1` for more details.
        """
        # TODO: check if oauthlib has already unquoted client_id and client_secret
        try:
            client_id = request.client_id
            client_secret = request.client_secret
        except AttributeError:
            return False

        if self._load_client(client_id, request) is None:
            logging.debug("Failed body auth: Application %s does not exists" % client_id)
            return False
        elif request.client.client_secret != client_secret:
            logging.debug("Failed body auth: wrong client secret %s" % client_secret)
            return False
        else:
            return True

    def _load_client(self, client_id, request):
        """
        If request.client was not set, load application instance for given client_id and store it
        in request.client
        """

        # we want to be sure that request has the client attribute!
        assert hasattr(request, "client"), "'request' instance has no 'client' attribute"

        request.client = request.client or self._client_interface.get(resource_uid=client_id)

        if not request.client:
            logging.debug("Failed body authentication: Application %s does not exist" % client_id)
            return None

        return request.client

    def client_authentication_required(self, request, *args, **kwargs):
        """
        Determine if the client has to be authenticated

        This method is called only for grant types that supports client authentication:
            * Authorization code grant
            * Resource owner password grant
            * Refresh token grant

        If the request contains authorization headers, always authenticate the client no matter
        the grant type.

        If the request does not contain authorization headers, proceed with authentication only if
        the client is of type `Confidential`.

        If something goes wrong, call oauthlib implementation of the method.
        """
        if self._extract_basic_auth(request):
            return True

        try:
            if request.client_id and request.client_secret:
                return True
        except AttributeError:
            logging.debug("Client id or client secret not provided, "
                          "proceed evaluating if authentication is required...")
            pass

        self._load_client(request.client_id, request)

        if request.client:
            return request.client.client_type == CLIENT_CONFIDENTIAL

        return super(OAuth2RequestValidator, self).client_authentication_required(request, *args, **kwargs)

    def authenticate_client(self, request, *args, **kwargs):
        """
        Check if client exists and it's authenticating itself as in rfc:`3.2.1`

        First we try to authenticate with HTTP Basic Auth, and that is the PREFERRED
        authentication method.
        Whether this fails we support including the client credentials in the request-body, but
        this method is NOT RECOMMENDED and SHOULD be limited to clients unable to directly utilize
        the HTTP Basic authentication scheme. See rfc:`2.3.1` for more details
        """
        authenticated = self._authenticate_basic_auth(request)

        if not authenticated:
            authenticated = self._authenticate_request_body(request)

        return authenticated

    def authenticate_client_id(self, client_id, request, *args, **kwargs):
        """
        If we are here, the client did not authenticate itself as in rfc:`3.2.1` and we can
        proceed only if the client exists and it's not of type 'Confidential'.
        Also assign Application instance to request.client.
        """
        if self._load_client(client_id, request) is not None:
            logging.debug("Application %s has type %s" % (client_id, request.client.client_type))
            return request.client.client_type != CLIENT_CONFIDENTIAL
        return False

    def confirm_redirect_uri(self, client_id, code, redirect_uri, client, *args, **kwargs):
        """
        Ensure the redirect_uri is listed in the Application instance redirect_uris field
        """
        grant = self._grant_interface.get(resource_uid=self._grant_interface._convert_client_id_to_datastore_key(code=code,
                                                                                                                 client_id=client_id))
        # TODO: move object function to this class
        return grant.redirect_uri_allowed(redirect_uri)

    def invalidate_authorization_code(self, client_id, code, request, *args, **kwargs):
        """
        Remove the temporary grant used to swap the authorization token
        """
        # TODO: this may need to use client_id instead of request.client.client_id
        grant = self._grant_interface.get(resource_uid=self._grant_interface._convert_client_id_to_datastore_key(code=code,
                                                                                                                 client_id=client_id))
        self._grant_interface.delete(resource_uid=grant.uid)

    def validate_client_id(self, client_id, request, *args, **kwargs):
        """
        Ensure an Application exists with given client_id. If it exists, it's assigned to
        request.client.
        """
        # TODO: modify with a SPI.get() call on the client_id; set client in request
        return self._load_client(client_id, request) is not None

    def get_default_redirect_uri(self, client_id, request, *args, **kwargs):
        return request.client.default_redirect_uri

    def validate_bearer_token(self, token, scopes, request):
        """
        When users try to access resources, check that provided token is valid
        """
        if not token:
            return False

        access_token = self._access_token_interface.get(resource_uid=token)

        if not access_token:
            return False

        client = self._client_interface.get(resource_uid=access_token.client_id)

        if access_token.is_valid(scopes):
            request.client = client
            request.user = access_token.guid
            request.scopes = scopes

            # this is needed by django rest framework
            request.access_token = access_token
            return True

        # The description may be overwritten here, but if both errors are present then we should get a new
        # one before validating the scopes - the process of renewing may correct the scope error.

        if not access_token.allow_scopes(scopes=scopes):
            request.error = 'insufficient_scope'
            request.error_description = 'Token does not allow specified scopes.'

        if access_token.is_expired():
            request.error = 'invalid_token'
            request.error_description = 'Token has expired.'

        return False

    def validate_code(self, client_id, code, client, request, *args, **kwargs):
        grant = self._grant_interface.get(resource_uid=self._grant_interface._convert_client_id_to_datastore_key(code=code,
                                                                                                                 client_id=client_id))

        if grant and not grant.is_expired():
            request.scopes = grant.scope.split(' ')
            request.user = grant.guid
            return True

        return False

    def validate_grant_type(self, client_id, grant_type, client, request, *args, **kwargs):
        """
        Validate both grant_type is a valid string and grant_type is allowed for current workflow
        """
        assert(grant_type in GRANT_TYPE_MAPPING)  # mapping misconfiguration
        return request.client.authorization_grant_type in GRANT_TYPE_MAPPING[grant_type]

    def validate_response_type(self, client_id, response_type, client, request, *args, **kwargs):
        """
        We currently do not support the Authorization Endpoint Response Types registry as in
        rfc:`8.4`, so validate the response_type only if it matches 'code' or 'token'
        """
        # TODO: remove the call to abstract application; move to settings/config
        if response_type == 'code':
            return client.authorization_grant_type == GRANT_AUTHORIZATION_CODE
        elif response_type == 'token':
            return client.authorization_grant_type == GRANT_IMPLICIT
        else:
            return False

    def validate_scopes(self, client_id, scopes, client, request, *args, **kwargs):
        """
        Ensure required scopes are permitted (as specified in the settings file)
        """
        # TODO: settings to global scope
        return set(scopes).issubset(set(_SCOPES))

    def get_default_scopes(self, client_id, request, *args, **kwargs):
        # TODO: settings to global scope
        return _SCOPES

    def validate_redirect_uri(self, client_id, redirect_uri, request, *args, **kwargs):
        return request.client.redirect_uri_allowed(redirect_uri)

    def save_authorization_code(self, client_id, code, request, *args, **kwargs):
        expires = datetime.utcnow() + timedelta(seconds=AUTHORIZATION_CODE_EXPIRE_SECONDS)

        grant = self._grant_interface.new(client_id=request.client.client_id,
                                          guid=request.user,
                                          code=code['code'],
                                          expires=expires,
                                          redirect_uri=request.redirect_uri,
                                          scope=' '.join(request.scopes))

        # TODO: check result of insert op?
        self._grant_interface.insert(resource_object=grant)

    def save_bearer_token(self, token, request, *args, **kwargs):
        """
        Save access and refresh token, If refresh token is issued, remove old refresh tokens as
        in rfc:`6`
        """
        if request.refresh_token:
            refresh_token = self._refresh_token_interface.get(resource_uid=request.refresh_token)

            if not refresh_token:
                # TODO being here would be very strange so log the error
                logging.error('Refresh token presented in request but no matching entity in datastore')
                assert()

            self._refresh_token_interface.delete(resource_uid=request.refresh_token)

        expires = datetime.utcnow() + timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS)
        if request.grant_type == 'client_credentials':
            request.user = None

        # TODO: change these init calls to use the SPI.new() methods, then use SPI.insert()

        access_token = self._access_token_interface.new(guid=request.user,
                                                        scope=token['scope'],
                                                        expires=expires,
                                                        token=token['access_token'],
                                                        client_id=request.client.client_id)

        # TODO: check the result of the insert
        access_token_insert_result = self._access_token_interface.insert(resource_object=access_token)

        if 'refresh_token' in token:
            refresh_token = self._refresh_token_interface.new(guid=request.user,
                                                              token=token['refresh_token'],
                                                              client_id=request.client.client_id,
                                                              access_token=token['access_token'])

            # TODO: check the result of the insert
            refresh_token_insert_result = self._refresh_token_interface.insert(resource_object=refresh_token)

        # TODO check out a more reliable way to communicate expire time to oauthlib
        token['expires_in'] = ACCESS_TOKEN_EXPIRE_SECONDS

    def revoke_token(self, token, token_type_hint, request, *args, **kwargs):
        """
        Revoke an access or refresh token.

        :param token: The token string.
        :param token_type_hint: access_token or refresh_token.
        :param request: The HTTP Request (oauthlib.common.Request)
        """
        if token_type_hint not in ['access_token', 'refresh_token']:
            token_type_hint = None

        token_types = {
            'access_token': self._access_token_interface,
            'refresh_token': self._refresh_token_interface,
        }

        token_type = token_types.get(token_type_hint, None)

        if token_type:
            stored_token = token_type.query(token=token)
            if stored_token:
                token_type.delete(resource_uid=stored_token.uid)
                return True
        else:
            stored_token = self._access_token_interface.get(resource_uid=token)
            if stored_token:
                self._access_token_interface.delete(resource_uid=token)
                return True
            else:
                stored_token = self._refresh_token_interface.get(resource_uid=token)
                self._refresh_token_interface.delete(resource_uid=token)
                return True

        return False

    def validate_user(self, username, password, client, request, *args, **kwargs):
        """
        Check username and password correspond to a valid and active User
        """
        if not signal('validate_user').has_receivers_for(self):
            raise koalacore.KoalaException(u'Configuration error in OAuth2RequestValidator - no validate_user receivers')

        try:
            signal('validate_user').send(self, username=username, password=password, **kwargs)
        except koalacore.UnauthorisedUser:
            logging.debug(u'User details were valid but permission was denied for login.')
            return False
        except koalacore.InvalidUser:
            logging.debug(u'User details were invalid.')
            return False
        else:
            return True

    def get_original_scopes(self, refresh_token, request, *args, **kwargs):
        # Avoid second query for RefreshToken since this method is invoked *after*
        # validate_refresh_token.
        rt = request.refresh_token_instance
        return rt.access_token.scope

    def validate_refresh_token(self, refresh_token, client, request, *args, **kwargs):
        """
        Check refresh_token exists and refers to the right client.
        Also attach User instance to the request object
        """
        # TODO: remove the try catch; if no object is found from the API then return False
        refresh_token = self._refresh_token_interface.get(resource_uid=request.refresh_token)

        if not refresh_token:
            return False

        request.user = refresh_token.guid
        request.refresh_token = refresh_token.token
        # Temporary store RefreshToken instance to be reused by get_original_scopes.
        request.refresh_token_instance = refresh_token
        return refresh_token.client_id == client.client_id


if "SERVER_SOFTWARE" in os.environ:
    if os.environ['SERVER_NAME'] in ['localhost', '127.0.0.1']:
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'
else:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'


VALIDATOR = OAuth2RequestValidator()


class OAuth2(object):
    _api_name = 'oauth2'
    _validator = VALIDATOR
    _server = WebApplicationServer(VALIDATOR)

    @classmethod
    def skip_authorization(cls, client_id):
        # send signal?
        client = cls._validator._client_interface.get(resource_uid=client_id)
        if client:
            return client.skip_authorization
        return True

    @classmethod
    def create_authorization_response(cls, uri, http_method='GET', body=None, headers=None, scopes=None,
                                      credentials=None):
        # send signal?
        return cls._server.create_authorization_response(uri, http_method, body, headers, scopes, credentials)

    @classmethod
    def validate_authorization_request(cls, uri, http_method='GET', body=None, headers=None):
        # send signal?
        return cls._server.validate_authorization_request(uri, http_method, body, headers)

    @classmethod
    def create_token_response(cls, uri, http_method='GET', body=None, headers=None, credentials=None):
        # send signal?
        return cls._server.create_token_response(uri, http_method, body, headers, credentials)

    @classmethod
    def create_revocation_response(cls, uri, http_method='POST', body=None, headers=None):
        # send signal?
        return cls._server.create_revocation_response(uri, headers=headers, body=body, http_method=http_method)

    @classmethod
    def verify_request(cls, uri, http_method='GET', body=None, headers=None, scopes=None):
        # send signal?
        return cls._server.verify_request(uri, http_method, body, headers, scopes)


class OAuth2ClientCredentials(OAuth2):
    _api_name = 'oauth2clientcredentials'
    _validator = VALIDATOR
    _server = BackendApplicationServer(VALIDATOR)
