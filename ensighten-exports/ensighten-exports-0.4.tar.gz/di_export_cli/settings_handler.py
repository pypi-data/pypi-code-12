import os
import urllib3
from swagger.swagger_client.configuration import Configuration
from swagger.swagger_client.rest import ApiException
from httprequests import HttpRequest


def update_configuration():
    update_api_url()
    update_auth_token()


def update_auth_token():
    # make call to auth with username and pw, then get header and put in api key
    response = HttpRequest(get_api_url()).get_auth_token(get_username(), get_password())
    Configuration().api_key['api_key'] = response.getheader('x-auth-token')


def update_api_url():
    Configuration().host = get_api_url()


def get_api_url():
    try:
        url = os.environ['DI_EXPORTS_URL']
        if url.endswith('/'):
            url = url[:-1]
        return os.environ['DI_EXPORTS_URL']
    except KeyError:
        # Default
        return 'https://api.data.ensighten.com'


def get_username():
    try:
        username = os.environ['DI_EXPORTS_USERNAME']
    except KeyError:
        return ""
    return username


def get_password():
    try:
        username = os.environ['DI_EXPORTS_PASSWORD']
    except KeyError:
        return ""
    return username


def settings_are_valid():
    if not get_username():
        print "Username is missing from environment variables"
        return False
    if not get_password():
        print "Password is missing from environment variables"
        return False
    try:
        update_auth_token()
        return True
    except ApiException as e:
        if e.status == 401:
            print 'Credentials invalid'
        else:
            print 'Error while validating credentials'
            print str(e)
        return False
    except urllib3.exceptions.MaxRetryError:
        print 'Could not establish connection'
        return False
    except Exception as e:
        print 'Could not validate credentials'
        print e
        return False

