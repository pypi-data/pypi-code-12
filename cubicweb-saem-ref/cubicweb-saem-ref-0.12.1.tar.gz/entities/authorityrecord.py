# copyright 2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-saem-ref entity's classes for AuthorityRecord."""

from cubicweb.entities import AnyEntity, fetch_config


class AuthorityRecord(AnyEntity):
    __regid__ = 'AuthorityRecord'
    fetch_attrs, cw_fetch_order = fetch_config(('name', 'agent_kind', 'ark'))

    @property
    def kind(self):
        """The kind of agent"""
        return self.agent_kind[0].name

    @property
    def printable_kind(self):
        """The kind of agent, for display"""
        return self.agent_kind[0].printable_value('name')


class AgentKind(AnyEntity):
    __regid__ = 'AgentKind'
    fetch_attrs, cw_fetch_order = fetch_config(('name',))


class ChronologicalRelation(AnyEntity):
    __regid__ = 'ChronologicalRelation'

    def dc_description(self):
        if self.description:
            return self.description


class EACResourceRelation(AnyEntity):
    __regid__ = 'EACResourceRelation'

    @property
    def record(self):
        return self.resource_relation_agent[0]

    @property
    def resource(self):
        return self.resource_relation_resource[0]

    def dc_title(self):
        agent_title = self.agent.dc_title()
        if self.agent_role:
            agent_title += u' (%s)' % self.printable_value('agent_role')
        resource_title = self.resource.dc_title()
        if self.resource_role:
            resource_title += u' (%s)' % self.printable_value('resource_role')
        return (self._cw._('Relation from %(from)s to %(to)s ') %
                {'from': agent_title,
                 'to': resource_title})


class SameAsMixIn(object):
    """Mix-in class for entity types supporting vocabulary_source and
    equivalent_concept relations.
    """

    @property
    def scheme(self):
        return self.vocabulary_source and self.vocabulary_source[0] or None

    @property
    def concept(self):
        return self.equivalent_concept and self.equivalent_concept[0] or None


class AgentPlace(SameAsMixIn, AnyEntity):
    __regid__ = 'AgentPlace'


class AgentFunction(SameAsMixIn, AnyEntity):
    __regid__ = 'AgentFunction'


class Mandate(SameAsMixIn, AnyEntity):
    __regid__ = 'Mandate'


class LegalStatus(SameAsMixIn, AnyEntity):
    __regid__ = 'LegalStatus'


class Occupation(SameAsMixIn, AnyEntity):
    __regid__ = 'Occupation'
