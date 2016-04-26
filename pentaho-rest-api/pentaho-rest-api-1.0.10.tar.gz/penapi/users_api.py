import logging
from pyexpat import ExpatError

import requests
import xmltodict as xmltodict

from constants import CREATE_USERS, LIST_USERS, USERS_USERNAME_VAR, USERS_PASSWORD_VAR

logger = logging.getLogger(__name__)


# TODO implement regex filtering
def list_all_users(pentaho=None, regex=None):
    """
    Get list of all users
    :param pentaho: the pentaho user object
    :return: (http/s Response, success/failure)
    :rtype: (String, list)
    """
    user_list = list()
    if not pentaho:
        raise ValueError("[ERROR] Pentaho object is missing ... ")
    response = requests.get(pentaho.get_user_urls(endpoint_type=LIST_USERS),
                            auth=(pentaho.pentaho_username, pentaho.pentaho_password))
    if response.status_code == 200:
        try:
            user_list = xmltodict.parse(response.text)['users']['user']
        except Exception, e:
            logger.exception(e)
    return response, user_list


def create_user(pentaho=None, username=None, password=None):
    """
    Create a user in pentaho
    :param pentaho: the pentaho object
    :param username: the username to assign to the user
    :param password: the password for the user
    :return: (http/s Response, success/failure )
    :rtype: (String, boolean)
    """
    created = False
    if not pentaho:
        raise ValueError("[ERROR] Pentaho object is missing ... ")
    if not username or not password:
        raise ValueError("[ERROR] user creation parameters missing ... ")
    user_credentials = {
        USERS_USERNAME_VAR: username,
        USERS_PASSWORD_VAR: password,
    }
    response = requests.put(pentaho.get_user_urls(endpoint_type=CREATE_USERS),
                            auth=(pentaho.pentaho_username, pentaho.pentaho_password),
                            json=user_credentials)
    if response.status_code == 200:
        created = True
    return response, created
