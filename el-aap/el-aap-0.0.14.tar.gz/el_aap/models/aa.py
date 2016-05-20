__author__ = 'schlitzer'

import logging
import re
import threading

from bottle import request, response
from cachetools import TTLCache

from el_aap_api.errors import *


class AuthenticationAuthorization(object):
    def __init__(self, users, roles, permissions):
        self.cache_user_password = TTLCache(maxsize=10240, ttl=120)
        self.cache_user_password_lock = threading.RLock()
        self.cache_user_roles = TTLCache(maxsize=10240, ttl=120)
        self.cache_user_roles_lock = threading.RLock()
        self.cache_role_permissions = TTLCache(maxsize=10240, ttl=120)
        self.cache_role_permissions_lock = threading.RLock()
        self.cache_permissions = TTLCache(maxsize=10240, ttl=120)
        self.cache_permissions_lock = threading.RLock()
        self.users = users
        self.roles = roles
        self.permissions = permissions
        self.log = logging.getLogger('el_aap')

    @method_wrapper
    def check_auth(self):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.debug("{0} authenticating request".format(request_id))
        user, password = request.auth or (None, None)
        if user is None or password is None:
            response.set_header('WWW-Authenticate',  'Basic realm="private"')
            raise BasicAuthenticationError
        credentials = {
            "user": user,
            "password": password
        }
        with self.cache_user_password_lock:
            if (user, password) in self.cache_user_password:
                self.log.debug("{0} successfully authenticated request from cache".format(request_id))
                return user
        try:
            self.users.check_credentials(credentials)
            with self.cache_user_password_lock:
                self.cache_user_password[(user, password)] = user
                self.log.debug("{0} successfully authenticated request from backend".format(request_id))
            return user
        except AuthenticationError:
            self.log.debug("{0} failed authenticated request {0}".format(request_id))
            response.set_header('WWW-Authenticate',  'Basic realm="private"')
            raise BasicAuthenticationError

    @method_wrapper
    def get_role_ids_by_user(self, user):
        request_id = request.environ.get('REQUEST_ID', None)
        with self.cache_user_roles_lock:
            if user in self.cache_user_roles:
                self.log.debug("{0} successfully fetched roles ids by user from cache".format(request_id))
                return self.cache_user_roles[user]
        roles = list()
        for role in self.roles.search(users=user, fields='_id')['results']:
            roles.append(role['_id'])
        self.log.debug("{0} successfully fetched roles ids by user from backend".format(request_id))
        with self.cache_user_roles_lock:
            self.cache_user_roles[user] = roles
        return roles

    @method_wrapper
    def get_permission_ids_by_role(self, role):
        request_id = request.environ.get('REQUEST_ID', None)
        with self.cache_role_permissions_lock:
            if role in self.cache_role_permissions:
                self.log.debug("{0} successfully fetched permissions ids by role from cache".format(request_id))
                return self.cache_role_permissions[role]
        permissions = list()
        for permission in self.permissions.search(roles=role, fields='_id')['results']:
            permissions.append(permission['_id'])
        self.log.debug("{0} successfully fetched permissions ids by role from backend".format(request_id))
        with self.cache_role_permissions_lock:
            self.cache_role_permissions[role] = permissions
        return permissions

    @method_wrapper
    def get_permissions(self, permissions):
        request_id = request.environ.get('REQUEST_ID', None)
        cached = list()
        non_cached = list()
        for permission in permissions:
            try:
                with self.cache_permissions_lock:
                    cached.append(self.cache_permissions[permission])
                    self.log.debug("{0} successfully fetched permission {1} from cache".format(request_id, permission))
            except KeyError:
                self.log.debug("{0} failed fetching permission {1} from cache".format(request_id, permission))
                non_cached.append(permission)
        if len(non_cached) == 0:
            return cached
        non_cached_str = '(' + '|'.join(non_cached) + ')'
        for permission in self.permissions.search(_ids=non_cached_str, fields='_id,permissions,scope')['results']:
            permission['re'] = re.compile('^'+permission['scope']+'$')
            with self.cache_permissions_lock:
                self.log.debug("{0} successfully fetched permission {1} from backend".format(request_id, permission['_id']))
                self.cache_permissions[permission['_id']] = permission
            cached.append(permission)
        return cached

    @method_wrapper
    def get_permissions_by_user(self, user):
        permission_ids = set()
        for role in self.get_role_ids_by_user(user):
            for permission_id in self.get_permission_ids_by_role(role):
                permission_ids.add(permission_id)
        permission_ids = list(permission_ids)
        permissions = self.get_permissions(permission_ids)
        return permissions

    @method_wrapper
    def require_permission(self, permission, index=None):
        request_id = request.environ.get('REQUEST_ID', None)
        user_perms = self.get_permissions_by_user(self.check_auth())
        self.log.debug("{0} authorizing request".format(request_id))
        for perm in user_perms:
            regex = perm['re']
            if index and not regex.match(index):
                self.log.debug(
                    "{0} access denied for request, permission rule {1} not matching"
                    " {2} with regex {3}, testing next rule".format(
                        request_id,
                        perm['_id'],
                        index,
                        regex
                    )
                )
                continue
            for priv in perm['permissions']:
                if permission.startswith(priv):
                    self.log.debug(
                        "{0} access granted for request, permission rule {1} "
                        "matching {2} with regex {3}".format(
                            request_id,
                            perm['_id'],
                            index,
                            regex
                        )
                    )
                    return True
        self.log.info("{0} failed authenticating request,  no more rules to try".format(request_id))
        raise PermError
