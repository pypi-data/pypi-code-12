# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

__docformat__ = "restructuredtext en"

from uuid import uuid4 as uuid

from six import text_type
from six.moves import range

from cubicweb import Unauthorized
from cubicweb.server import hook
from cubicweb.predicates import is_instance

from cubes.signedrequest.authplugin import UserSecretKeyAuthentifier

class ServerStartupHook(hook.Hook):
    """register authentifier at startup"""
    __regid__ = 'signedrequest.secretkeyinit'
    events = ('server_startup',)

    def __call__(self):
        self.debug('registering secret key authentifier')
        self.repo.system_source.add_authentifier(UserSecretKeyAuthentifier())


class CreateAuthTokenHook(hook.Hook):
    """Generate random secret token"""
    __regid__ = 'signedrequest.createauthtoken'
    __select__ = hook.Hook.__select__ & is_instance('AuthToken')
    events = ('before_add_entity',)

    def __call__(self):
        edited = self.entity.cw_edited
        token = u''.join([uuid().hex for __ in range(4)]) # 128 chars len string
        edited['token'] = token
        edited['id'] = edited.get('id') or text_type(uuid().hex)
        edited.setdefault('token_for_user', self._cw.user.eid)
