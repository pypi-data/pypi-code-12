"""
Sets of configuration values for a GA4GH server.
Any of these values may be overridden by a file on the path
given by the environment variable GA4GH_CONFIGURATION.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime


class BaseConfig(object):
    """
    Simplest default server configuration.
    """
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB
    MAX_RESPONSE_LENGTH = 1024 * 1024  # 1MB
    REQUEST_VALIDATION = True
    RESPONSE_VALIDATION = False
    DEFAULT_PAGE_SIZE = 100
    DATA_SOURCE = "empty://"

    # Options for the simulated backend.
    SIMULATED_BACKEND_RANDOM_SEED = 0
    SIMULATED_BACKEND_NUM_CALLS = 1
    SIMULATED_BACKEND_VARIANT_DENSITY = 0.5
    SIMULATED_BACKEND_NUM_VARIANT_SETS = 1
    SIMULATED_BACKEND_NUM_REFERENCE_SETS = 1
    SIMULATED_BACKEND_NUM_REFERENCES_PER_REFERENCE_SET = 1
    SIMULATED_BACKEND_NUM_ALIGNMENTS_PER_READ_GROUP = 2
    SIMULATED_BACKEND_NUM_READ_GROUPS_PER_READ_GROUP_SET = 2

    FILE_HANDLE_CACHE_MAX_SIZE = 50

    LANDING_MESSAGE_HTML = "landing_message.html"


class DevelopmentConfig(BaseConfig):
    """
    Configuration used for development.
    """
    DATA_SOURCE = "ga4gh-example-data"
    DEBUG = True


class LocalOidConfig(DevelopmentConfig):
    """
    Configuration used for developing against a local OIDC server
    """
    OIDC_PROVIDER = "https://localhost:8443"


class SimulatedConfig(BaseConfig):
    """
    A configuration that uses simulated backing for testing.
    """
    DATA_SOURCE = "simulated://"
    DEBUG = True
    REQUEST_VALIDATION = True
    RESPONSE_VALIDATION = True


class ProductionConfig(BaseConfig):
    """
    Configuration that is a good basis for production deployments.
    """
    REQUEST_VALIDATION = True
    # We should complain loudly if data source is not set, rather than
    # mysteriously serve no data.
    DATA_SOURCE = None


class GoogleOidcConfig(ProductionConfig):
    """
    Configuration that is a good basis for production deployments using
    Google as the authentication provider.
    """
    OIDC_PROVIDER = "https://accounts.google.com"
    OIDC_REDIRECT_URI = "https://localhost/oauth2callback"
    OIDC_CLIENT_ID = "XXX"
    OIDC_CLIENT_SECRET = "XXX"


class TestConfig(BaseConfig):
    """
    Configuration used in frontend unit tests.
    """
    TESTING = True
    REQUEST_VALIDATION = True
    RESPONSE_VALIDATION = True


class TestOidcConfig(TestConfig):
    OIDC_PROVIDER = "https://accounts.example.com"
    OIDC_CLIENT_ID = "XXX"
    OIDC_CLIENT_SECRET = "XXX"
    OIDC_AUTHZ_ENDPOINT = "https://accounts.example.com/auth"
    OIDC_TOKEN_ENDPOINT = "https://accounts.example.com/token"
    OIDC_TOKEN_REV_ENDPOINT = "https://accounts.example.com/revoke"


class FlaskDefaultConfig(object):
    """
    The default values for the Flask config.
    Only used in testing.
    """
    APPLICATION_ROOT = None
    DEBUG = False
    JSONIFY_PRETTYPRINT_REGULAR = True
    JSON_AS_ASCII = True
    JSON_SORT_KEYS = True
    LOGGER_NAME = 'ga4gh.frontend'
    MAX_CONTENT_LENGTH = None
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(31)
    PREFERRED_URL_SCHEME = 'http'
    PRESERVE_CONTEXT_ON_EXCEPTION = None
    PROPAGATE_EXCEPTIONS = None
    SECRET_KEY = None
    SEND_FILE_MAX_AGE_DEFAULT = 43200
    SERVER_NAME = None
    SESSION_COOKIE_DOMAIN = None
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_NAME = 'session'
    SESSION_COOKIE_PATH = None
    SESSION_COOKIE_SECURE = False
    TESTING = False
    TRAP_BAD_REQUEST_ERRORS = False
    TRAP_HTTP_EXCEPTIONS = False
    USE_X_SENDFILE = False
