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
"""cubicweb-saem-ref test for OAI-PMH export"""

from collections import namedtuple
from datetime import date, datetime, timedelta
from functools import wraps
import time

from dateutil.parser import parse as parse_date
from lxml import etree
import pytz

from logilab.common import tempattr

from cubicweb.devtools.testlib import CubicWebTC

from cubes.oaipmh import isodate
from cubes.oaipmh.entities import OAIComponent
from cubes.oaipmh.views import OAIError, OAIRequest

import testutils


EntityInfo = namedtuple('EntityInfo', ['ark', 'url', 'eid'])


def publish_entity(entity):
    """Fire "publish" transition for `entity`."""
    entity.cw_adapt_to('IWorkflowable').fire_transition('publish')
    entity._cw.commit()


def deprecate_entity(entity):
    """Fire "deprecate" transition for `entity`."""
    entity.cw_adapt_to('IWorkflowable').fire_transition('deprecate')
    entity._cw.commit()


class OAITestMixin(object):

    def oai_component(self, cnx):
        """Return the "oai" component"""
        return self.vreg['components'].select('oai', cnx)


class OAIComponentTC(CubicWebTC, OAITestMixin):

    def test_registered(self):
        with self.admin_access.repo_cnx() as cnx:
            oai = self.oai_component(cnx)
            setspecs = oai.__setspecs__
            self.assertCountEqual(setspecs.keys(),
                                  ['agent', 'conceptscheme', 'profile', 'concept'])
            self.assertCountEqual(setspecs['agent'].keys(),
                                  ['kind', 'role'])
            self.assertCountEqual(setspecs['profile'].keys(),
                                  ['transferring_agent'])
            self.assertEqual(setspecs['conceptscheme'].keys(), [])

    def test_match_setspec(self):
        with self.admin_access.repo_cnx() as cnx:
            oai = self.oai_component(cnx)
            with self.assertRaises(ValueError) as cm:
                oai.match_setspec(u'cwuser')
            self.assertIn('no setspec matching cwuser', str(cm.exception))

    def test_setspecs(self):
        with self.admin_access.repo_cnx() as cnx:
            arch = testutils.agent(cnx, u'arch', archival_roles=[u'archival'])
            ark = testutils.agent(cnx, u'dep', archival_roles=[u'deposit'],
                                  archival_agent=arch).ark
            scheme = testutils.setup_scheme(cnx, u'test', u'lab')
            cnx.commit()
            publish_entity(scheme)
            expected = (
                'agent',
                'agent:kind:person', 'agent:kind:authority', 'agent:kind:family',
                'agent:role:producer', 'agent:role:deposit',
                'agent:role:archival', 'agent:role:control',
                'agent:role:enquirer', 'agent:role:seda-actor',
                'conceptscheme',
                'profile', 'profile:transferring_agent:%s' % ark,
                'concept', 'concept:in_scheme:%s' % scheme.ark
            )
            oai = self.oai_component(cnx)
            setspecs = [x[0] for x in oai.setspecs()]
            self.assertCountEqual(setspecs, expected)


def setup_agents(cnx):
    """Create three agents (alice, bob and draft), publish alice and bob but not draft, and return
    the (ark, url, eid) attributes of alice and bob.
    """
    alice = testutils.agent(cnx, u'alice', archival_roles=[u'producer'])
    cnx.commit()
    publish_entity(alice)
    bob = testutils.agent(cnx, u'bob', archival_roles=[u'enquirer'],
                          kind=u'family')
    cnx.commit()
    publish_entity(bob)
    testutils.agent(cnx, u'draft', kind=u'family',
                    archival_roles=[u'enquirer'])
    cnx.commit()
    return (
        EntityInfo(alice.ark, alice.absolute_url(), alice.eid),
        EntityInfo(bob.ark, bob.absolute_url(), bob.eid),
    )


class OAIRequestTC(CubicWebTC):

    def test_rset_from_setspec(self):
        """Test `rset_from_setspec` function for exceptions."""
        with self.admin_access.repo_cnx() as cnx:
            return setup_agents(cnx)
        with self.admin_access.web_request() as req:
            for setspec, msg in [
                ('agent:zen', 'invalid set specifier agent:zen'),
                ('agent:role:control', (
                    'The combination of the values of the from, until, and '
                    'set arguments results in an empty list.')),
                ('conceptscheme:haha', 'invalid set specifier conceptscheme:haha'),
                ('scregneugneu', 'invalid set specifier scregneugneu'),
            ]:
                self.set_description(setspec)
                oairq = OAIRequest('http://testing.fr', setspec=setspec)
                with self.assertRaises(OAIError) as cm:
                    oairq.rset_from_setspec(req)
                self.assertEqual(cm.exception.errors, {'noRecordsMatch': msg})

    def test_rset_from_setspec_token(self):
        with self.admin_access.repo_cnx() as cnx:
            alice, bob = setup_agents(cnx)

        def oairq(**kwargs):
            return OAIRequest('http://testing.fr', setspec='agent', **kwargs)

        with self.admin_access.web_request() as req:
            with tempattr(OAIComponent, 'max_result_size', 1):
                rset, token = oairq().rset_from_setspec(req)
                self.assertEqual(len(rset), 1)
                self.assertEqual(token, str(bob.eid))
                rset, token = oairq(resumption_token=str(bob.eid)).rset_from_setspec(req)
                self.assertEqual(len(rset), 1)
                self.assertIsNone(token)
            # All results are returned, the resumptionToken is None.
            rset, token = oairq().rset_from_setspec(req)
            self.assertEqual(len(rset), 2)
            self.assertIsNone(token)
            # and this, even if the user specified an input token.
            rset, token = oairq(resumption_token='1').rset_from_setspec(req)
            self.assertEqual(len(rset), 2)
            self.assertIsNone(token)


def no_validate_xml(method):
    """Disable XML schema validation, often because the underlying metadata
    part of the response (RDF, XSD) is not validable (or we don't know how to
    do it).
    """
    @wraps(method)
    def wrapper(self):
        self._validate_xml = False
        self._debug_xml = True
        return method(self)
    return wrapper


class OAIPMHViewsTC(CubicWebTC, OAITestMixin, testutils.XmlTestMixin):

    _validate_xml = True
    _debug_xml = False

    def oai_request(self, req, **formparams):
        req.form.update(formparams)
        out = self.app_handle_request(req, 'oai')
        if self._validate_xml:
            self.assertXmlValid(out, self.datapath('OAI-PMH.xsd'), debug=self._debug_xml)
        return out

    def _setup_agents(self, **kwargs):
        with self.admin_access.repo_cnx() as cnx:
            return setup_agents(cnx, **kwargs)

    def test_xml_attributes_and_namespaces(self):
        """Check XML attributes and namespace declaration of the response."""
        with self.admin_access.web_request() as req:
            # simple request, generating an error but enough to get a properly
            # formatter response.
            result = self.oai_request(req)
            xml = etree.fromstring(result)
            nsmap = {None: 'http://www.openarchives.org/OAI/2.0/',
                     'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}
            self.assertEqual(xml.nsmap, nsmap)
            attrib = {
                '{http://www.w3.org/2001/XMLSchema-instance}schemaLocation': ' '.join(
                    ['http://www.openarchives.org/OAI/2.0/',
                     'http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd']),
            }
            self.assertEqual(xml.attrib, attrib)

    def test_responsedate(self):
        """Check <responseDate>"""
        with self.admin_access.web_request() as req:
            # Simple request, generating an error but enough to get a properly
            # formatter response.
            now = datetime.utcnow()
            result = self.oai_request(req)
        # Check tzinfo abbreviation is present (Z for UTC).
        self.assertIn('<responseDate>{0}</responseDate>'.format(isodate(now)),
                      result)

    def _setup_agents_deleted(self):
        alice, bob = self._setup_agents()
        with self.admin_access.repo_cnx() as cnx:
            entity = cnx.entity_from_eid(bob.eid)
            # ensure transition date is greater by at least 1s
            time.sleep(1)
            date_before = entity.modification_date.replace(tzinfo=pytz.utc)
            deprecate_entity(entity)
        return alice, bob, date_before

    def _setup_schemes(self):
        with self.admin_access.repo_cnx() as cnx:
            pscheme = testutils.setup_scheme(cnx, u'public',
                                             u'public label', u'other public label')
            # draft ConceptScheme
            dscheme = testutils.setup_scheme(cnx, u'draft',
                                             u'draft label', u'other draft label')
            cnx.commit()
            publish_entity(pscheme)
            return (
                EntityInfo(pscheme.ark, pscheme.absolute_url(), pscheme.eid),
                EntityInfo(dscheme.ark, dscheme.absolute_url(), dscheme.eid),
            )

    def test_noverb(self):
        with self.admin_access.web_request() as req:
            result = self.oai_request(req)
        self.assertIn('<request>http://testing.fr/cubicweb/oai</request>',
                      result)
        self.assertIn('<error code="badVerb">no verb specified</error',
                      result)

    def test_badverb(self):
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='coucou')
        self.assertIn('<request>http://testing.fr/cubicweb/oai</request>',
                      result)
        self.assertIn('<error code="badVerb">illegal verb "coucou"</error>',
                      result)

    # some of our setspecs (those with an ARK inside are not valid)
    @no_validate_xml
    def test_listsets(self):
        pscheme, dscheme = self._setup_schemes()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListSets')
        self.assertIn('<request verb="ListSets">http://testing.fr/cubicweb/oai</request>',
                      result)
        for spec in ('agent', 'conceptscheme', 'profile', 'concept'):
            self.assertIn('<setSpec>{0}</setSpec>'.format(spec),
                          result)
        self.assertIn(('<setSpec>agent:role:deposit</setSpec>'
                       '<setName>An agent with deposit archival role</setName>'),
                      result)
        self.assertIn('<setSpec>concept:in_scheme:{0}</setSpec>'.format(pscheme.ark),
                      result)
        self.assertNotIn(dscheme.ark, result)

    def test_listidentifiers_noset(self):
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers')
        self.assertIn('<request>http://testing.fr/cubicweb/oai</request>',
                      result)
        self.assertIn(('<error code="badArgument">'
                       'ListIdentifiers verb requires "set" restriction'
                       '</error>'),
                      result)

    def _setup_profile(self):
        """Create a "published" SEDAProfile and return its identifier"""
        with self.admin_access.repo_cnx() as cnx:
            profile = testutils.setup_seda_profile(cnx)
            cnx.commit()
            publish_entity(profile)
            return profile.ark

    def test_resumptiontoken_listidentifiers(self):
        alice, bob = self._setup_agents()

        def check_request(expected_arks, token=None):
            with self.admin_access.web_request() as req:
                result = self.oai_request(
                    req, verb='ListIdentifiers', set='agent',
                    resumptionToken=token)
                # Ensure there are as many <identifier> tag than expected items.
                self.assertEqual(result.count('<identifier>'), len(expected_arks))
                for ark in expected_arks:
                    self.assertIn(
                        '<identifier>ark:/{0}</identifier>'.format(ark), result)
                return result

        self.set_description('less results than pagination limit')
        result = check_request([alice.ark, bob.ark])
        # All results returned, no resumptionToken is request -> no
        # resumptionToken in response.
        self.assertNotIn('resumptionToken', result)
        with tempattr(OAIComponent, 'max_result_size', 1):
            self.set_description('max_result_size = 1, 1st batch')
            result = check_request([alice.ark])
            self.set_description('token + expirationDate')
            root = etree.fromstring(result)
            token = root.find('.//{%s}resumptionToken' % root.nsmap[None])
            date = parse_date(token.attrib['expirationDate'])
            self.assertLess(datetime.now(pytz.utc) + timedelta(hours=1) - date,
                            timedelta(seconds=1))
            self.assertEqual(token.text, str(bob.eid))
            self.set_description('max_result_size = 1, 2nd batch')
            result = check_request([bob.ark], token=str(bob.eid))
            self.set_description('max_result_size = 1, no more result')
            # No more results -> empty resumptionToken.
            self.assertIn('<resumptionToken/>', result)
            # Empty result, probably a badResumptionToken.
            result = check_request([], token=str(bob.eid + 1))
            self.assertIn('badResumptionToken', result)

    def test_listidentifiers(self):
        alice, bob = [x.ark for x in self._setup_agents()]
        profile_id = self._setup_profile()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers', set='agent')
            self.assertIn('<identifier>ark:/{0}</identifier>'.format(bob), result)
            self.assertIn('<identifier>ark:/{0}</identifier>'.format(alice), result)
            draft = req.execute('Any A WHERE X ark A, X name "draft"')[0][0]
            self.assertNotIn(draft, result)
            result = self.oai_request(req, verb='ListIdentifiers',
                                      set='agent:role:producer')
            self.assertIn('<identifier>ark:/{0}</identifier>'.format(alice),
                          result)
            self.assertNotIn('<identifier>ark:/{0}</identifier>'.format(bob),
                             result)
            result = self.oai_request(req, verb='ListIdentifiers', set='agent:kind:person')
            self.assertIn('<identifier>ark:/{0}</identifier>'.format(alice), result)
            self.assertNotIn('<identifier>ark:/{0}</identifier>'.format(bob), result)
            result = self.oai_request(req, verb='ListIdentifiers', set='conceptscheme')
            result = self.oai_request(req, verb='ListIdentifiers', set='profile')
            self.assertIn('<identifier>ark:/{0}</identifier>'.format(profile_id), result)

    def test_listidentifiers_setspec_wfstate(self):
        """Check workflow state condition is statisfied with a multi-level
        setspec `agent:role:enquirer`.
        """
        alice, bob = [x.ark for x in self._setup_agents()]
        self._setup_profile()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers',
                                      set='agent:role:enquirer')
            self.assertIn('<identifier>ark:/{0}</identifier>'.format(bob), result)
            draft = req.execute('Any A WHERE X ark A, X name "draft"')[0][0]
            self.assertNotIn(draft, result)

    def test_listidentifiers_deleted(self):
        """Check <header> element (status attribute, datestamp) for deleted
        records in ListIdentifiers response.
        """
        alice, bob, date_before = self._setup_agents_deleted()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers', set='agent')
            self.assertIn(
                '<identifier>ark:/{0}</identifier>'.format(bob.ark), result)
            self.assertIn('<header status="deleted">', result)
            root = etree.fromstring(result)
            ns = root.nsmap[None]
            # only one <header status="..."> element
            header, = root.findall('.//{%s}header[@status]' % ns)
            datestamp = header.find('{%s}datestamp' % ns).text
            date = parse_date(datestamp)
            self.assertGreater(date, date_before.replace(microsecond=0))

    def test_listrecords_noset(self):
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListRecords')
        self.assertIn('<request>http://testing.fr/cubicweb/oai</request>',
                      result)
        self.assertIn(('<error code="badArgument">'
                       'ListRecords verb requires "set" restriction'
                       '</error>'),
                      result)

    @no_validate_xml
    def test_listrecords(self):
        alice, bob = self._setup_agents()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListRecords', set='agent')
            self.assertIn(
                '<rdf:Description rdf:about="{0}">'.format(bob.url), result)
            self.assertIn(
                '<rdf:Description rdf:about="{0}">'.format(alice.url), result)
            draft = req.execute('Any A WHERE X ark A, X name "draft"')[0][0]
            self.assertNotIn(draft, result)
            result = self.oai_request(
                req, verb='ListRecords', set='agent:role:producer')
            self.assertIn(
                '<rdf:Description rdf:about="{0}">'.format(alice.url), result)
            self.assertNotIn(bob.url, result)
            result = self.oai_request(req, verb='ListRecords', set='agent:kind:person')
            self.assertIn(
                '<rdf:Description rdf:about="{0}">'.format(alice.url), result)
            self.assertNotIn(bob.url, result)

    @no_validate_xml
    def test_listrecord_deleted(self):
        """Check absence of <metadata> or <about> elements for deleted
        records in ListRecords response.
        """
        alice, bob, _ = self._setup_agents_deleted()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListRecords', set='agent')
            # no metadata for bob
            self.assertNotIn(
                '<rdf:Description rdf:about="{0}">'.format(bob.url), result)
            # but record present
            self.assertIn('<identifier>ark:/{0}</identifier>'.format(bob.ark), result)
            self.assertIn(
                '<rdf:Description rdf:about="{0}">'.format(alice.url), result)

    @no_validate_xml
    def test_listrecords_profile(self):
        self._setup_profile()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListRecords', set='profile')
        # Just ensure a SEDA profile (xsd) is present in response.
        self.assertIn('<metadata><xsd:schema', result)
        self.assertIn('fr:gouv:ae:archive:draft:standard_echange_v0.2', result)

    @no_validate_xml
    def test_listidentifiers_profile_setspec(self):
        """Check setspec restriction for SEDAProfile."""
        profile_id = self._setup_profile()
        profile2_id = self._setup_profile()
        with self.admin_access.web_request() as req:
            transferring_agent_ark = req.execute(
                'Any K WHERE P ark "%s", P seda_transferring_agent A, A ark K'
                % profile_id)[0][0]
            result = self.oai_request(
                req, verb='ListIdentifiers',
                set='profile:transferring_agent:' + transferring_agent_ark)
            self.assertIn('<identifier>ark:/{0}</identifier>'.format(profile_id), result)
            self.assertNotIn(profile2_id, result)
        # Check that without a setspec, we get all profiles.
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers', set='profile')
            self.assertIn('<identifier>ark:/{0}</identifier>'.format(profile_id), result)
            self.assertIn('<identifier>ark:/{0}</identifier>'.format(profile2_id), result)

    @no_validate_xml
    def test_getrecord_profile(self):
        profile_id = self._setup_profile()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='GetRecord')
            self.assertIn('<error code="badArgument">', result)
            result = self.oai_request(req, verb='GetRecord', identifier='999')
            self.assertIn('<error code="idDoesNotExist"', result)
            result = self.oai_request(req, verb='GetRecord', identifier='ark:/' + profile_id)
            self.assertIn('<metadata><xsd:schema', result)
            self.assertIn('fr:gouv:ae:archive:draft:standard_echange_v0.2', result)

    @no_validate_xml
    def test_getrecord_agent(self):
        self._debug_xml = True
        with self.admin_access.repo_cnx() as cnx:
            agent = testutils.agent(cnx, u'toto')
            cnx.commit()
            publish_entity(agent)
            ark = agent.ark
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='GetRecord', identifier='ark:/' + ark)
            self.assertIn('name>toto</', result)
            self.assertIn('<rdf:type rdf:resource="http://xmlns.com/foaf/0.1/Person"/>',
                          result)

    def test_getrecord_deleted(self):
        """Check absence of <metadata> or <about> elements for deleted
        records in GetRecord response.
        """
        alice, bob, _ = self._setup_agents_deleted()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='GetRecord', identifier='ark:/' + bob.ark)
            # record is present
            self.assertIn('<identifier>ark:/{0}</identifier>'.format(bob.ark), result)
            # but not data
            self.assertNotIn('metadata', result)
            self.assertNotIn('rdf', result)

    def test_getrecord_draft(self):
        self._setup_agents()
        with self.admin_access.web_request() as req:
            draft = req.execute('Any A WHERE X ark A, X name "draft"')[0][0]
            result = self.oai_request(req, verb='GetRecord', identifier='ark:/' + draft)
            self.assertIn('idDoesNotExist', result)

    def test_from_until_error(self):
        with self.admin_access.web_request() as req:
            dates = {'from': date(2013, 1, 2).isoformat(),
                     'until': date(2011, 1, 2).isoformat()}
            result = self.oai_request(req, verb='ListIdentifiers', set='agent',
                                      **dates)
            self.assertIn('<error code="badArgument">the from argument', result)

    def test_from_until_listidentifiers(self):
        alice, bob = self._setup_agents()
        with self.admin_access.repo_cnx() as cnx:
            alice_date = cnx.entity_from_eid(alice.eid).modification_date
            bob_date = alice_date + timedelta(seconds=2)
            cnx.entity_from_eid(bob.eid).cw_set(modification_date=bob_date)
            cnx.commit()
        in_between_date = isodate(alice_date + timedelta(seconds=1))
        self.set_description('from only')
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers', set='agent',
                                      **{'from': in_between_date})
            self.assertIn(bob.ark, result)
            self.assertNotIn(alice.ark, result)
        self.set_description('until only')
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers', set='agent',
                                      **{'until': in_between_date})
            self.assertNotIn(bob.ark, result)
            self.assertIn(alice.ark, result)
        self.set_description('from and until')
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers', set='agent',
                                      **{'from': '1970-12-1',
                                         'until': '2099-01-02'})
            self.assertIn(bob.ark, result)
            self.assertIn(alice.ark, result)
        self.set_description('no record match')
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers', set='agent',
                                      **{'until': '1970-12-31'})
            self.assertIn('<error code="noRecordsMatch">The combi', result)

    def test_from_until_listidentifiers_setspec(self):
        """Check from/until restriction with a multi-level setspec
        `agent:kind:family`
        """
        alice, bob = self._setup_agents()
        with self.admin_access.repo_cnx() as cnx:
            bob_date = cnx.entity_from_eid(bob.eid).modification_date
            marcel = cnx.find('Agent', name=u'draft').one()
            publish_entity(marcel)
            marcel_date = bob_date + timedelta(seconds=2)
            marcel.cw_set(name=u'marcel', modification_date=marcel_date)
            marcel_ark = marcel.ark
            cnx.commit()
        in_between_date = isodate(bob_date + timedelta(seconds=1))
        self.set_description('from only')
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers',
                                      set='agent:kind:family',
                                      **{'from': in_between_date})
            self.assertNotIn(bob.ark, result)
            self.assertIn(marcel_ark, result)
            self.assertNotIn(alice.ark, result)
        self.set_description('until only')
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers',
                                      set='agent:kind:family',
                                      **{'until': in_between_date})
            self.assertIn(bob.ark, result)
            self.assertNotIn(marcel_ark, result)
            self.assertNotIn(alice.ark, result)
        self.set_description('from and until')
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers',
                                      set='agent:kind:family',
                                      **{'from': '1970-12-1',
                                         'until': '2099-01-02'})
            self.assertIn(bob.ark, result)
            self.assertIn(marcel_ark, result)
            self.assertNotIn(alice.ark, result)
        self.set_description('no record match')
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers',
                                      set='agent:kind:family',
                                      **{'until': '1970-12-31'})
            self.assertIn('<error code="noRecordsMatch">The combi', result)


if __name__ == '__main__':
    import unittest
    unittest.main()
