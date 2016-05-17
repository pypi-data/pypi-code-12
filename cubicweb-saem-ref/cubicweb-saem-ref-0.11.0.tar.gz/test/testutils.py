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
"""cubicweb-saem_ref common test tools"""

import unittest
from doctest import Example

from lxml import etree
from lxml.doctestcompare import LXMLOutputChecker

from cubicweb import NoResultError


def agent(cnx, name, kind=u'person', archival_roles=(), **kwargs):
    """Return an Agent with specified kind, name and archival roles."""
    kind_eid = cnx.find('AgentKind', name=kind)[0][0]
    if archival_roles:
        if len(archival_roles) > 1:
            rset = cnx.execute('Any X WHERE X is ArchivalRole, X name IN (%s)' %
                               ','.join('"%s"' % r for r in archival_roles))
        else:
            rset = cnx.execute('Any X WHERE X is ArchivalRole, X name "%s"' %
                               archival_roles[0])
        roles_eid = [x for x, in rset.rows]
    else:
        roles_eid = ()
    if 'authority' not in kwargs:
        authority = cnx.find('Authority', name=u'Default authority').one()
        kwargs['authority'] = authority
    else:
        authority = kwargs['authority']
        if isinstance(authority, int):
            authority = cnx.entity_from_eid(authority)
    if not authority.ark_naa:
        with cnx.security_enabled(False, False):
            authority.cw_set(ark_naa=naa(cnx))
    return cnx.create_entity('Agent', name=name, agent_kind=kind_eid,
                             archival_role=roles_eid, **kwargs)


def naa(cnx):
    try:
        return cnx.find('ArkNameAssigningAuthority').one()
    except NoResultError:
        return cnx.create_entity('ArkNameAssigningAuthority', who=u'TEST', what=0)


def authority_with_naa(cnx):
    authority = cnx.find('Authority', name=u'Default authority').one()
    if not authority.ark_naa:
        authority.cw_set(ark_naa=naa(cnx))
    return authority


def setup_scheme(cnx, title, *labels):
    """Return info new concept scheme"""
    scheme = cnx.create_entity('ConceptScheme', title=title, ark_naa=naa(cnx))
    for label in labels:
        scheme.add_concept(label)
    return scheme


def setup_seda_agents(cnx):
    """Return two agents, one with the 'deposit' archival role, another with
    the 'archival' archival role.
    """
    alice = agent(cnx, u'alice')
    city = agent(cnx, u'New York city', kind=u'authority',
                 archival_roles=[u'archival'], contact_point=alice)
    bob = agent(cnx, u'bob', archival_roles=['deposit'], archival_agent=city)
    return bob, city


def setup_seda_profile(cnx, complete_archive=True, **kwargs):
    """Return a minimal SEDA profile with agents and a profile archive (with or without content
    description and access restriction code according to the `complete_archive` flag).
    """
    transferring_agent, archival_agent = setup_seda_agents(cnx)
    create_entity = cnx.create_entity
    profile = create_entity('SEDAProfile', seda_transferring_agent=transferring_agent,
                            ark_naa=naa(cnx), **kwargs)
    kwargs = {}
    if complete_archive:
        kwargs['seda_content_description'] = create_entity(
            'SEDAContentDescription',
            seda_description_level=create_entity('SEDADescriptionLevel'))
        kwargs['seda_access_restriction_code'] = create_entity('SEDAAccessRestrictionCode')
    create_entity('ProfileArchiveObject', seda_name=create_entity('SEDAName'),
                  seda_parent=profile, **kwargs)
    return profile


def publishable_profile(cnx, **kwargs):
    """Return a minimal SEDA profile that may be published."""
    create_entity = cnx.create_entity
    profile = create_entity('SEDAProfile', ark_naa=naa(cnx), **kwargs)
    create_entity('ProfileArchiveObject',
                  seda_parent=profile,
                  seda_name=create_entity('SEDAName'),
                  seda_content_description=create_entity(
                      'SEDAContentDescription',
                      seda_description_level=create_entity('SEDADescriptionLevel')),
                  seda_access_restriction_code=create_entity('SEDAAccessRestrictionCode'))
    return profile


def concept(cnx, label):
    """Return concept entity with the given preferred label (expected to be unique)."""
    return cnx.execute('Concept X WHERE X preferred_label L, L label %(label)s',
                       {'label': label}).one()


def seda_scheme(cnx, rtype, label_kind, *labels, **kwargs):
    """Build a ConceptScheme with `scheme_relation` pointing to `rtype` along
    with concepts with `labels` of `label_kind`.
    """
    rtype_eid = cnx.find('CWRType', name=rtype)[0][0]
    scheme = cnx.create_entity('ConceptScheme',
                               title=kwargs.get('scheme_title'),
                               scheme_relation=rtype_eid,
                               ark_naa=naa(cnx))
    for label in labels:
        scheme.add_concept(label, kind=label_kind)
    return scheme


#
# XML helpers
#

def xmlpp(string):
    """Parse and pretty-print XML data from `string`."""
    print etree.tostring(etree.fromstring(string), pretty_print=True)


class XmlTestMixin(unittest.TestCase):
    """Mixin class provinding additional assertion methods for checking XML data."""

    def assertXmlEqual(self, actual, expected):
        """Check that both XML strings represent the same XML tree."""
        checker = LXMLOutputChecker()
        if not checker.check_output(expected, actual, 0):
            message = checker.output_difference(Example("", expected), actual, 0)
            self.fail(message)

    def assertXmlValid(self, xml_data, xsd_filename, debug=False):
        """Validate an XML file (.xml) according to an XML schema (.xsd)."""
        with open(xsd_filename) as xsd:
            xmlschema = etree.XMLSchema(etree.parse(xsd))
        # Pretty-print xml_data to get meaningfull line information.
        xml_data = etree.tostring(etree.fromstring(xml_data), pretty_print=True)
        xml_data = etree.fromstring(xml_data)
        if debug and not xmlschema.validate(xml_data):
            xmlpp(xml_data)
        xmlschema.assertValid(xml_data)
