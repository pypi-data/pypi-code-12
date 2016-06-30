#   Copyright 2016 University of Lancaster
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import logging

from kallithea import EXTERN_TYPE_INTERNAL
from kallithea.lib import auth_modules
from kallithea.lib.compat import formatted_json, hybrid_property
from kallithea.model.db import User

log = logging.getLogger(__name__)


class KallitheaAuthPlugin(auth_modules.KallitheaAuthPluginBase):
    def __init__(self):
        pass

    @hybrid_property
    def name(self):
        return EXTERN_TYPE_INTERNAL

    @hybrid_property
    def is_container_auth(self):
        return True

    def settings(self):
        return []

    def get_user(self, username=None, **kwargs):
        # Try REMOTE_USER
        environ = kwargs.get('environ', {})
        remote_user = environ.get('REMOTE_USER')
        if remote_user:
            username = remote_user

        return super(KallitheaAuthPlugin, self).get_user(username)

    def user_activation_state(self):
        def_user_perms = User.get_default_user().AuthUser.permissions['global']
        return 'hg.register.auto_activate' in def_user_perms

    def accepts(self, user, accepts_empty=True):
        """
        Custom accepts for this auth that doesn't accept empty users. We
        know that user exisits in database.
        """
        return super(KallitheaAuthPlugin, self).accepts(user,
                                                        accepts_empty=False)

    def auth(self, userobj, username, password, settings, **kwargs):
        # Try REMOTE_USER
        environ = kwargs.get('environ', {})
        remote_user = environ.get('REMOTE_USER')
        if remote_user:
            log.info("Got remote user %s" % (remote_user, ))
            username = remote_user
            userobj = User.get_by_username(remote_user)

        if not userobj:
            log.debug('userobj was:%s skipping' % (userobj, ))
            return None
        if userobj.extern_type != self.name:
            log.warn("userobj:%s extern_type mismatch got:`%s` expected:`%s`"
                     % (userobj, userobj.extern_type, self.name))
            return None

        user_attrs = {
            "username": userobj.username,
            "firstname": userobj.firstname,
            "lastname": userobj.lastname,
            "groups": [],
            "email": userobj.email,
            "admin": userobj.admin,
            "active": userobj.active,
            "active_from_extern": userobj.active,
            "extern_name": userobj.user_id,
            'extern_type': userobj.extern_type,
        }

        log.debug(formatted_json(user_attrs))
        if not userobj.active:
            log.warning('user %s tried auth but is disabled' % (username, ))
            return None

        # Authenticated via remote_user?
        if remote_user:
            log.info(
                'user %s authenticated via remote_user' %
                (user_attrs['username'], ))
            return user_attrs

        from kallithea.lib import auth
        password_match = auth.KallitheaCrypto.hash_check(
            password, userobj.password)
        if userobj.username == username and password_match:
            log.info(
                'user %s authenticated correctly' %
                (user_attrs['username'], ))
            return user_attrs

        log.error("user %s had a bad password" % username)
        return None

    def get_managed_fields(self):
        # Note: 'username' should only be editable (at least for user) if
        # self registration is enabled
        return []
