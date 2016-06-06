import logging
import re
import xmltodict

from constants import (
    TAB_SEPARATOR,
    PENTAHO_USERS_ENDPOINT_API,
    CREATE_USERS,
    LIST_USERS,
    CHANGE_USER_PASSWORD,
    DELETE_USERS,
    USERS_USERNAME_VAR,
    USERS_PASSWORD_VAR,
    USERS_NEW_PASSWORD_VAR,
    USERS_OLD_PASSWORD_VAR,
    USERS_DELETE_VAR
)

from penapi.base_api import PentahoBaseAPI

try:
    logger = logging.getLogger(__name__)
except Exception:
    logger = logging.getLogger("PENTAHO_USERS_API")


class PentahoUsersAPI(PentahoBaseAPI):

    def list(self, regex=None):
        """
        Get list of all users
        :param pentaho: the pentaho user object
        :return: success/failure
        :rtype: list
        """
        user_list = list()
        response = self._pentaho.make_call(PENTAHO_USERS_ENDPOINT_API, LIST_USERS)
        if response.status_code == 200:
            try:
                user_list = xmltodict.parse(response.text)['userList']['users']
            except Exception, e:
                logger.exception(e)
        if regex:
            user_list = [v for v in user_list if re.match(regex, v)]
        return user_list

    def create(self, username=None, password=None):
        """
        Create a user in pentaho
        :param username: the username to assign to the user
        :param password: the password for the user
        :return: success/failure
        :rtype: boolean
        """
        if not username or not password:
            raise ValueError("[ERROR] user creation parameters missing... ")
        user_credentials = {
            USERS_USERNAME_VAR: username,
            USERS_PASSWORD_VAR: password,
        }
        response = self._pentaho.make_call(PENTAHO_USERS_ENDPOINT_API, CREATE_USERS,
                                           json=user_credentials)
        return response.status_code == 200

    def change_password(self, username, old_password, new_password):
        """
        Change password for a user in pentaho
        :param username: user to change the password
        :param old_password: old password
        :param new_password: new password
        :return: success/failure
        :rtype: boolean
        """
        user_password_change = {
            USERS_USERNAME_VAR: username,
            USERS_OLD_PASSWORD_VAR: old_password,
            USERS_NEW_PASSWORD_VAR: new_password
        }
        response = self._pentaho.make_call(PENTAHO_USERS_ENDPOINT_API, CHANGE_USER_PASSWORD,
                                           json=user_password_change)
        return response.status_code == 200

    def delete(self, usernames=None):
        """
        Delete a user in pentaho
        :param usernames: the usernames to delete (string or list)
        :return: success/failure
        :rtype: boolean
        """
        if not usernames:
            raise ValueError("[ERROR] user delete parameters missing... ")
        if type(usernames) is list:
            usernames = TAB_SEPARATOR.join(usernames)
        response = self._pentaho.make_call(PENTAHO_USERS_ENDPOINT_API, DELETE_USERS,
                                           params={USERS_DELETE_VAR: usernames})
        return response.status_code == 200
