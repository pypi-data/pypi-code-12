import logging
import re
import xmltodict

from constants import (
    TAB_SEPARATOR,
    PENTAHO_ROLES_ENDPOINT_API,
    USERS_USERNAME_VAR,
    ROLES_ASSIGN_VAR,
    GET_ROLES_FOR_USER,
    ASSIGN_ROLE_TO_USER,
    REMOVE_ROLE_FROM_USER
)

from penapi.base_api import PentahoBaseAPI

logger = logging.getLogger(__name__)


class PentahoRolesAPI(PentahoBaseAPI):

    def list_for_user(self, username):
        """
        Get roles for a user
        :param username: user to get roles
        :return: success/failure
        :rtype: list
        """
        role_list = list()
        response = self._pentaho.make_call(PENTAHO_ROLES_ENDPOINT_API, GET_ROLES_FOR_USER,
                                           params={USERS_USERNAME_VAR: username})
        if response.status_code == 200:
            try:
                role_list = xmltodict.parse(response.text)['roleList']['roles']
            except Exception, e:
                logger.exception(e)
        return role_list

    def assign_to_user(self, username, roles):
        """
        Asign roles to a user
        :param username: user to assign roles
        :param roles: list of roles to assign to the user
        :return: success/failure
        :rtype: list
        """
        if isinstance(roles, basestring):
            raise ValueError("[ERROR] roles parameter must be iterable but not a string...")
        response = self._pentaho.make_call(PENTAHO_ROLES_ENDPOINT_API, ASSIGN_ROLE_TO_USER,
                                           params={USERS_USERNAME_VAR: username,
                                                   ROLES_ASSIGN_VAR: TAB_SEPARATOR.join(roles)})
        return response.status_code == 200

    def remove_from_user(self, username, roles):
        """
        Remove roles from a user
        :param username: user to assign roles
        :param roles: list of roles to remove from the user
        :return: success/failure
        :rtype: list
        """
        if isinstance(roles, basestring):
            raise ValueError("[ERROR] roles parameter must be iterable but not a string...")
        response = self._pentaho.make_call(PENTAHO_ROLES_ENDPOINT_API, REMOVE_ROLE_FROM_USER,
                                           params={USERS_USERNAME_VAR: username,
                                                   ROLES_ASSIGN_VAR: TAB_SEPARATOR.join(roles)})
        return response.status_code == 200

