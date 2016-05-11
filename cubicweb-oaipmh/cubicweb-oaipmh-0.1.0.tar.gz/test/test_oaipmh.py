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
"""cubicweb-saem-ref test for OAI-PMH export"""
from __future__ import print_function

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


def agent(cnx, name=None, kind=u'person', **kwargs):
    return cnx.create_entity('Agent', name=name,
                             kind=cnx.create_entity('AgentKind', name=kind),
                             **kwargs)


def xmlview_snippet(cnx, eid):
    """Return a snippet of xmlitem view for entity with `eid`."""
    entity = cnx.entity_from_eid(eid)
    return u'<%s eid="%s" cwuri="%s"' % (entity.cw_etype, entity.eid,
                                         entity.cwuri)


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
                                  ['agent', 'activity', 'thing'])
            self.assertCountEqual(setspecs['agent'].keys(),
                                  ['kind'])
            self.assertCountEqual(setspecs['activity'].keys(),
                                  ['associated_with'])
            self.assertCountEqual(setspecs['thing'].keys(), [])

    def test_match_setspec(self):
        with self.admin_access.repo_cnx() as cnx:
            oai = self.oai_component(cnx)
            with self.assertRaises(ValueError) as cm:
                oai.match_setspec(u'cwuser')
            self.assertIn('no setspec matching cwuser', str(cm.exception))

    def test_setspecs(self):
        with self.admin_access.repo_cnx() as cnx:
            bob = agent(cnx, u'bob')
            cnx.commit()
            expected = (
                'agent',
                'agent:kind:person',
                'activity', 'activity:associated_with:%s' % bob.name,
                'thing',
            )
            oai = self.oai_component(cnx)
            setspecs = [x[0] for x in oai.setspecs()]
            self.assertCountEqual(setspecs, expected)

    def test_setspecs_no_identifier_attribute(self):
        """An entity without an "identifier_attribute" set should not yield a
        setspec for related entities.
        """
        with self.admin_access.repo_cnx() as cnx:
            agent(cnx)
            cnx.commit()
            expected = (
                'agent',
                'agent:kind:person',
                'activity',
                'thing',
            )
            oai = self.oai_component(cnx)
            setspecs = [x[0] for x in oai.setspecs()]
            self.assertCountEqual(setspecs, expected)


class OAIRequestTC(CubicWebTC):

    def test_rset_from_setspec(self):
        """Test `rset_from_setspec` function for exceptions."""
        with self.admin_access.repo_cnx() as cnx:
            agent(cnx, u'bob')
            agent(cnx, u'New York City', kind=u'authority')
            cnx.commit()
        with self.admin_access.web_request() as req:
            for setspec, msg in [
                ('agent:zen', 'invalid set specifier agent:zen'),
                ('agent:kind:family', (
                    'The combination of the values of the from, until, and '
                    'set arguments results in an empty list.')),
                ('scregneugneu', 'invalid set specifier scregneugneu'),
            ]:
                oairq = OAIRequest('http://testing.fr', setspec=setspec)
                with self.assertRaises(OAIError) as cm:
                    oairq.rset_from_setspec(req)
                self.assertEqual(cm.exception.errors, {'noRecordsMatch': msg})

    def test_rset_from_setspec_token(self):
        with self.admin_access.repo_cnx() as cnx:
            agent(cnx, u'bob')
            simpsons = agent(cnx, u'The Simpson', kind=u'family')
            cnx.commit()

        def oairq(**kwargs):
            return OAIRequest('http://testing.fr', setspec='agent', **kwargs)

        with self.admin_access.web_request() as req:
            with tempattr(OAIComponent, 'max_result_size', 1):
                rset, token = oairq().rset_from_setspec(req)
                self.assertEqual(len(rset), 1)
                self.assertEqual(token, str(simpsons.eid))
                rset, token = oairq(resumption_token=token).rset_from_setspec(req)
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


def xmlpp(string):
    """Parse and pretty-print XML data from `string`."""
    print(etree.tostring(etree.fromstring(string), pretty_print=True))


class OAIPMHViewsTC(CubicWebTC, OAITestMixin):

    _validate_xml = True
    _debug_xml = True

    def assertXmlValid(self, xml_data, xsd_filename, debug=False):
        """Validate an XML file (.xml) according to an XML schema (.xsd)."""
        with open(xsd_filename) as xsd:
            xmlschema = etree.XMLSchema(etree.parse(xsd))
        # Pretty-print xml_data to get meaningfull line information.
        xml_data = etree.tostring(etree.fromstring(xml_data), pretty_print=True)
        xml_data = etree.fromstring(xml_data)
        if debug and not xmlschema.validate(xml_data):
            print(xml_data)
        xmlschema.assertValid(xml_data)

    def oai_request(self, req, **formparams):
        req.form.update(formparams)
        out = self.app_handle_request(req, 'oai')
        if self._validate_xml:
            self.assertXmlValid(out, self.datapath('OAI-PMH.xsd'), debug=self._debug_xml)
        return out

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

    def test_listsets(self):
        with self.admin_access.cnx() as cnx:
            agent(cnx, u'bob')
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListSets')
        self.assertIn('<request verb="ListSets">http://testing.fr/cubicweb/oai</request>',
                      result)
        for spec in ('agent', 'activity'):
            self.assertIn('<setSpec>{0}</setSpec>'.format(spec),
                          result)
        self.assertIn(('<setSpec>agent:kind:person</setSpec>'
                       '<setName>An agent of kind person</setName>'),
                      result)
        self.assertIn(('<setSpec>activity:associated_with:bob</setSpec>'
                       '<setName>Agent bob\'s activities</setName>'),
                      result)

    def test_listidentifiers_noset(self):
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers')
        self.assertIn('<request>http://testing.fr/cubicweb/oai</request>',
                      result)
        self.assertIn(('<error code="badArgument">'
                       'ListIdentifiers verb requires "set" restriction'
                       '</error>'),
                      result)

    def test_resumptiontoken_listidentifiers(self):
        with self.admin_access.cnx() as cnx:
            alice = agent(cnx, u'alice')
            bob = agent(cnx, u'bob')
            cnx.commit()

        def check_request(expected_identifiers, token=None):
            with self.admin_access.web_request() as req:
                result = self.oai_request(
                    req, verb='ListIdentifiers', set='agent',
                    resumptionToken=token)
                # Ensure there are as many <identifier> tag than expected items.
                self.assertEqual(
                    result.count('<identifier>'), len(expected_identifiers))
                for identifier in expected_identifiers:
                    self.assertIn(
                        '<identifier>{0}</identifier>'.format(identifier), result)
                return result

        result = check_request([alice.eid, bob.eid])
        # All results returned, no resumptionToken is request -> no
        # resumptionToken in response.
        self.assertNotIn('resumptionToken', result)
        with tempattr(OAIComponent, 'max_result_size', 1):
            result = check_request([alice.eid])
            root = etree.fromstring(result)
            token = root.find('.//{%s}resumptionToken' % root.nsmap[None])
            date = parse_date(token.attrib['expirationDate'])
            self.assertLess(datetime.now(pytz.utc) + timedelta(hours=1) - date,
                            timedelta(seconds=1))
            self.assertEqual(token.text, str(bob.eid))
            result = check_request([bob.eid], token=str(bob.eid))
            # No more results -> empty resumptionToken.
            self.assertIn('<resumptionToken/>', result)
            # Empty result, probably a badResumptionToken.
            result = check_request([], token=str(bob.eid + 1))
            self.assertIn('badResumptionToken', result)

    def test_listidentifiers(self):
        with self.admin_access.cnx() as cnx:
            alice = agent(cnx, u'alice').eid
            newyork = agent(cnx, u'New York City', u'authority').eid
            cnx.create_entity('Thing', identifier=u'007')
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers', set='agent')
            self.assertIn('<identifier>{0}</identifier>'.format(newyork), result)
            self.assertIn('<identifier>{0}</identifier>'.format(alice), result)
            self.assertEqual(result.count('<identifier>'), 2)
            result = self.oai_request(req, verb='ListIdentifiers',
                                      set='agent:kind:person')
            self.assertIn('<identifier>{0}</identifier>'.format(alice),
                          result)
            self.assertNotIn('<identifier>{0}</identifier>'.format(newyork),
                             result)
            result = self.oai_request(req, verb='ListIdentifiers',
                                      set='activity')
            self.assertIn('<error code="noRecordsMatch">', result)
            result = self.oai_request(req, verb='ListIdentifiers', set='thing')
            self.assertIn('<identifier>007</identifier>', result)

    def test_listidentifiers_deleted(self):
        """Check <header> element (status attribute, datestamp) for deleted
        records in ListIdentifiers response.
        """
        with self.admin_access.cnx() as cnx:
            cnx.create_entity('Thing', identifier=u'a')
            deleted = cnx.create_entity('Thing', identifier=u'b')
            date_before = deleted.modification_date.replace(tzinfo=pytz.utc)
            cnx.commit()
            time.sleep(1)
            deleted.cw_set(deleted=True)
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers', set='thing')
            self.assertIn('<identifier>a</identifier>', result)
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
        with self.admin_access.cnx() as cnx:
            alice = agent(cnx, u'alice')
            newyork = agent(cnx, u'New York', kind=u'authority')
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListRecords', set='agent')
            self.assertIn(xmlview_snippet(req, alice.eid), result)
            self.assertIn(str(newyork.eid), result)
            result = self.oai_request(req, verb='ListRecords',
                                      set='agent:kind:person')
            self.assertIn(xmlview_snippet(req, alice.eid), result)
            self.assertNotIn(str(newyork.eid), result)

    @no_validate_xml
    def test_listrecord_deleted(self):
        """Check absence of <metadata> or <about> elements for deleted
        records in ListRecords response.
        """
        with self.admin_access.cnx() as cnx:
            thing = cnx.create_entity('Thing', identifier=u'a')
            deleted = cnx.create_entity('Thing', identifier=u'b',
                                        deleted=True)
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListRecords', set='thing')
            self.assertNotIn(xmlview_snippet(req, deleted.eid),
                             result)
            # but record present
            self.assertIn('<identifier>b</identifier>', result)
            # not-deleted thing is present with metadata.
            self.assertIn(xmlview_snippet(req, thing.eid), result)

    @no_validate_xml
    def test_getrecord(self):
        with self.admin_access.repo_cnx() as cnx:
            thing = cnx.create_entity('Thing', identifier=u'aaa')
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='GetRecord',
                                      identifier=u'aaa')
            self.assertIn(xmlview_snippet(req, thing.eid), result)

    @no_validate_xml
    def test_getrecord_agent(self):
        with self.admin_access.repo_cnx() as cnx:
            bob = agent(cnx, u'bob')
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='GetRecord',
                                      identifier=str(bob.eid))
            self.assertIn(u'bob', result)

    def test_getrecord_deleted(self):
        """Check absence of <metadata> or <about> elements for deleted
        records in GetRecord response.
        """
        with self.admin_access.cnx() as cnx:
            cnx.create_entity('Thing', identifier=u'd', deleted=True)
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='GetRecord', identifier=u'd')
            # record is present
            self.assertIn('<identifier>d</identifier>', result)
            # but not data
            self.assertNotIn('metadata', result)
            self.assertNotIn('<Thing', result)

    def test_getrecord_inexistant(self):
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='GetRecord', identifier=u'z')
            self.assertIn('idDoesNotExist', result)

    def test_from_until_error(self):
        with self.admin_access.web_request() as req:
            dates = {'from': date(2013, 1, 2).isoformat(),
                     'until': date(2011, 1, 2).isoformat()}
            result = self.oai_request(req, verb='ListIdentifiers', set='agent',
                                      **dates)
            self.assertIn('<error code="badArgument">the from argument', result)

    def test_from_until_listidentifiers(self):
        with self.admin_access.cnx() as cnx:
            alice = agent(cnx, u'alice')
            bob = agent(cnx, u'bob')
            cnx.commit()
        with self.admin_access.repo_cnx() as cnx:
            alice_date = cnx.entity_from_eid(alice.eid).modification_date
            bob_date = alice_date + timedelta(seconds=2)
            cnx.entity_from_eid(bob.eid).cw_set(modification_date=bob_date)
            cnx.commit()
        in_between_date = isodate(alice_date + timedelta(seconds=1))
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers', set='agent',
                                      **{'from': in_between_date})
            self.assertIn(str(bob.eid), result)
            self.assertNotIn(str(alice.eid), result)
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers', set='agent',
                                      **{'until': in_between_date})
            self.assertNotIn(str(bob.eid), result)
            self.assertIn(str(alice.eid), result)
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers', set='agent',
                                      **{'from': '1970-12-1',
                                         'until': '2099-01-02'})
            self.assertIn(str(bob.eid), result)
            self.assertIn(str(alice.eid), result)
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers', set='agent',
                                      **{'until': '1970-12-31'})
            self.assertIn('<error code="noRecordsMatch">The combi', result)

    def test_from_until_listidentifiers_setspec(self):
        """Check from/until restriction with a multi-level setspec
        `agent:kind:family`
        """
        with self.admin_access.cnx() as cnx:
            alice = agent(cnx, u'alice')
            simpsons = agent(cnx, u'The Simpson', u'family')
            adams = agent(cnx, u'Adams family', u'family')
            cnx.commit()
        with self.admin_access.cnx() as cnx:
            simpsons_date = cnx.entity_from_eid(simpsons.eid).modification_date
            adams = cnx.entity_from_eid(adams.eid)
            adams_date = simpsons_date + timedelta(seconds=2)
            adams.cw_set(modification_date=adams_date)
            cnx.commit()
        in_between_date = isodate(simpsons_date + timedelta(seconds=1))
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers',
                                      set='agent:kind:family',
                                      **{'from': in_between_date})
            self.assertNotIn(str(simpsons.eid), result)
            self.assertIn(str(adams.eid), result)
            self.assertNotIn(str(alice.eid), result)
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers',
                                      set='agent:kind:family',
                                      **{'until': in_between_date})
            self.assertIn(str(simpsons.eid), result)
            self.assertNotIn(str(adams.eid), result)
            self.assertNotIn(str(alice.eid), result)
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers',
                                      set='agent:kind:family',
                                      **{'from': '1970-12-1',
                                         'until': '2099-01-02'})
            self.assertIn(str(simpsons.eid), result)
            self.assertIn(str(adams.eid), result)
            self.assertNotIn(str(alice.eid), result)
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers',
                                      set='agent:kind:family',
                                      **{'until': '1970-12-31'})
            self.assertIn('<error code="noRecordsMatch">The combi', result)


if __name__ == '__main__':
    import unittest
    unittest.main()
