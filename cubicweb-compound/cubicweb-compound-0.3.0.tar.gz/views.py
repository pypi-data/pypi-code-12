# copyright 2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-compound views/forms/actions/components for web ui"""

from cubicweb import neg_role
from cubicweb.web import Redirect
from cubicweb.predicates import (one_line_rset, adaptable, has_permission,
                                 match_form_params)
from cubicweb.web.controller import Controller
from cubicweb.web.views import actions, ibreadcrumbs

from cubes.compound.entities import copy_entity


_ = unicode


class CloneAction(actions.CopyAction):
    """Just a copy action (copy is handled by edit controller below) named 'clone'."""
    __select__ = (actions.CopyAction.__select__ & one_line_rset() &
                  adaptable('IClonable') & has_permission('add'))
    title = _('clone')

    def url(self):
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        iclone = entity.cw_adapt_to('IClonable')
        linkto = '%s:%s:%s' % (iclone.rtype, entity.eid, neg_role(iclone.role))
        return entity.absolute_url(vid='copy', __linkto=linkto)


actions.CopyAction.__select__ &= ~adaptable('IClonable')


class CloneController(Controller):
    """Controller handling cloning of the original entity (with `eid` passed
    in form parameters). Redirects to the cloned entity primary view.
    """
    __regid__ = 'compound.clone'
    __select__ = Controller.__select__ & match_form_params('eid')

    def publish(self, rset=None):
        eid = int(self._cw.form['eid'])
        original = self._cw.entity_from_eid(eid)
        iclone = original.cw_adapt_to('IClonable')
        rtype = (iclone.rtype if iclone.role == 'object'
                 else 'reverse_' + iclone.rtype)
        kwargs = {rtype: eid}
        clone = copy_entity(original, **kwargs)
        msg = self._cw._('clone of entity #%d created' % eid)
        raise Redirect(clone.absolute_url(__message=msg))


class IContainedBreadcrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    """Breadcrumbs adapter returning parent defined by the IContained adapter
    """
    __select__ = ibreadcrumbs.IBreadCrumbsAdapter.__select__ & adaptable('IContained')

    def parent_entity(self):
        contained = self.entity.cw_adapt_to('IContained')
        return contained.parent
