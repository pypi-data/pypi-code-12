"""
constants.py

Author: Jacob Harding

Holds string literals associated with Harvest REST API.
"""

HARVEST_STATUS_URL = 'http://www.harveststatus.com/api/v2/status.json'
HARVEST_OAUTH_AUTHORIZE_PATH = "oauth2/authorize"
HARVEST_OAUTH_TOKEN_PATH = "/oauth2/token"
HOURS_OF_VALID_TOKEN = 18

class HTTPContentType:
    """Class hold to content type strings as a constant."""
    XML = "application/xml"
    JSON = "application/json"
    FORM_ENCODED = 'application/x-www-form-urlencoded'

class HTTPHeader:
    """String literals to represent header keys and values"""
    ACCEPT = 'Accept'
    AUTH = 'Authorization'
    CONTENT_TYPE = 'Content-Type'

    BASIC_AUTH_FORMAT = 'Basic {0}'

class OauthKey:
    """Keys expected using the oauth operations of Harvest.
    The same keys are expected in the kwargs when instantiating the HarvestClient.
    """
    CLIENT_ID = 'client_id'
    RESPONSE_TYPE = 'response_type'
    REDIRECT_URI = 'redirect_uri'
    CODE = 'code'
    CLIENT_SECRET = 'client_secret'
    GRANT_TYPE = 'grant_type'
    ACCESS_TOKEN = 'access_token'
    REFRESH_TOKEN = 'refresh_token'

class OauthValue:
    """Values expected when using oauth with the Harvest API."""
    CODE = 'code'
    AUTH_CODE = 'authorization_code'
    REFRESH_TOKEN = 'refresh_token'

class BasicKey:
    """Keys expected to be be submitted in the kwargs of the HarvestClient when using Basic Auth."""
    EMAIL = 'email'
    PASSWORD = 'password'
 