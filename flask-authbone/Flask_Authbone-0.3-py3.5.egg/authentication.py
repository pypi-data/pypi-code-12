from functools import wraps
from flask import g


class Authenticator(object):

    IDENTITY_KEY = 'auth_identity'

    def __init__(self, auth_data_getter=None, authenticate_func=None):
        if auth_data_getter:
            self.auth_data_getter = auth_data_getter
        if authenticate_func:
            self.authenticate = authenticate_func

    def is_authenticated(self):
        return hasattr(g, self.IDENTITY_KEY)

    def get_identity(self):
        return getattr(g, self.IDENTITY_KEY)

    def set_identity(self, identity):
        setattr(g, self.IDENTITY_KEY, identity)

    currIdentity = property(get_identity, set_identity)

    def auth_data_getter(self):
        raise NotImplemented()

    def authenticate(self):
        raise NotImplemented()

    def auth_data_validator(self, auth_data):
        return self.authenticate(auth_data)

    def identity_elaborator(self, identity):
        self.currIdentity = identity

    def perform_authentication(self):
        if self.is_authenticated():
            return self.currIdentity
        auth_data = self.auth_data_getter()
        if auth_data is None:
            return self.bad_auth_data_callback()
        identity = self.auth_data_validator(auth_data)
        if identity is None:
            return self.not_authenticated_callback()
        self.identity_elaborator(identity)
        return identity

    def requires_authentication(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            self.perform_authentication()
            return f(*args, **kwargs)
        return decorated

    def bad_auth_data_callback(self):
        raise AuthDataDecodingException()

    def not_authenticated_callback(self):
        raise NotAuthenticatedException()


class AuthDataDecodingException(Exception):
    pass


class NotAuthenticatedException(Exception):
    pass
