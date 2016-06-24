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
"""cubicweb-compound specific hooks and operations"""


from cubicweb.predicates import objectify_predicate
from cubicweb.server import hook

from cubes.compound.entities import IClonableAdapter


@objectify_predicate
def match_clone_rtype(cls, req, *args, **kwargs):
    """Return 1 if `rtype` found in context matches any of the registed clone
    relations in IClonableAdapter.
    """
    rtype = kwargs['rtype']
    if rtype in IClonableAdapter.clone_relations:
        return 1
    return 0


class CloneEntityHook(hook.Hook):
    """Trigger cloning of an entity upon addition of a <clone_of> relation.
    """
    __regid__ = 'compound.clone_entity_hook'
    __select__ = hook.Hook.__select__ & match_clone_rtype()
    events = ('after_add_relation', )

    def __call__(self):
        original_role = IClonableAdapter.clone_relations[self.rtype]
        if original_role == 'subject':
            original = self._cw.entity_from_eid(self.eidfrom)
            clone = self._cw.entity_from_eid(self.eidto)
        else:
            original = self._cw.entity_from_eid(self.eidto)
            clone = self._cw.entity_from_eid(self.eidfrom)
        adapted = original.cw_adapt_to('IClonable')
        adapted.clone_into(clone)
