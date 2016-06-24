# copyright 2015-2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-saem-ref Web Services"""

from cubicweb.view import View
from cubicweb.predicates import match_http_method, match_user_groups
from cubicweb.web.views import json

from cubes.saem_ref import user_has_naa


class AssignArkWebService(json.JsonMixIn, View):
    """JSON view to assign a new Ark for external usage."""

    __regid__ = 'saem_ref.ws.ark'
    __select__ = (match_user_groups('users', 'managers')
                  & user_has_naa()
                  & match_http_method('POST'))

    # XXX could check Accept=application/json
    def call(self):
        self.wdata([{'ark': self._cw.call_service('saem_ref.attribute-ark')}])


class AssignArkWebServiceNoConfiguredUser(AssignArkWebService):
    __select__ = match_user_groups('users', 'managers') & ~user_has_naa()

    def call(self):
        self.wdata([{'error': 'User is not associated to an authority.'}])


class AssignArkWebServiceNonPOST(AssignArkWebService):
    __select__ = match_user_groups('users', 'managers')

    def call(self):
        self.wdata([{'error': 'This service is only accessible using POST.'}])


class AssignArkWebServiceNonAuthenticated(AssignArkWebService):
    __select__ = ~match_user_groups('users', 'managers')

    def call(self):
        self.wdata([{'error': 'This service requires authentication.'}])
