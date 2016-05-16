#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_requests_reviewer
----------------------------------

Tests for `requests_reviewer` module.
"""

from __future__ import unicode_literals

import logging
import unittest
import requests
import requests_mock

from requests_reviewer import review_response, rules, rules_helpers

logger = logging.getLogger(name=__name__)


@requests_mock.Mocker()
class TestRequests_reviewer(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_regular_http_code_returned(self, mockr):
        url = "http://csirtfoundry.com"
        mockr.register_uri('GET', url, text='returned')
        r = requests.get(url)
        revised_code = review_response(r)

        self.assertEqual(r.status_code, 200)
        self.assertEqual(revised_code.code, 200)
        self.assertEqual(revised_code.reason, None)

    def test_must_pass_requests_response(self, mockr):
        mockresp = "Not a response obj"

        try:
            review_response(mockresp)
            assert(False)
        except ValueError:
            assert(True)

    def test_header_match_present(self, mockr):
        url = "http://csirtfoundry.com"

        _rules = [{
            rules.NAME: "Test rule",
            rules.PRED: lambda r: rules_helpers.match_header(r, "X-Match", "Hasit"),
            rules.RESULT_CODE: 500,
            rules.RESULT_REASON: "X-Match header",
        }]

        mockr.register_uri(
            'GET', url, text='returned', headers={'X-Match': "Hasit"})
        r = requests.get(url)
        resp = review_response(r, rules=_rules)

        self.assertEqual(resp.code, 500)
        self.assertEqual(resp.reason, "X-Match header")
        self.assertEqual(resp.updated, True)

    def test_header_match_missing(self, mockr):
        url = "http://csirtfoundry.com"

        _rules = [{
            rules.NAME: "Test rule",
            rules.PRED: lambda r: rules_helpers.match_header(r, "X-Match", "Hasit"),
            rules.RESULT_CODE: 500,
            rules.RESULT_REASON: "X-Match header",
        }]

        mockr.register_uri(
            'GET', url, text='returned', headers={'X-Nosuch': "Hasit"})
        r = requests.get(url)
        resp = review_response(r, rules=_rules)

        self.assertEqual(resp.code, 200)
        self.assertEqual(resp.reason, None)
        self.assertEqual(resp.updated, False)

    def test_header_case_insensitive_match(self, mockr):
        url = "http://csirtfoundry.com"

        _rules = [{
            rules.NAME: "Test rule",
            rules.PRED: lambda r: rules_helpers.match_header(r, "Location", "/abc"),
            rules.RESULT_CODE: 500,
            rules.RESULT_REASON: "Location header",
        }]

        mockr.register_uri(
            'GET', url, text='returned', headers={'location': "/abc"})
        r = requests.get(url)
        resp = review_response(r, rules=_rules)

        self.assertEqual(resp.code, 500)
        self.assertEqual(resp.reason, "Location header")

    def test_header_no_match(self, mockr):
        url = "http://csirtfoundry.com"

        _rules = [{
            rules.NAME: "Test rule",
            rules.PRED: lambda r: rules_helpers.match_header(r, "X-Match", "Hasit"),
            rules.RESULT_CODE: 500,
            rules.RESULT_REASON: "X-Match header",
        }]

        mockr.register_uri(
            'GET', url, text='returned', headers={'X-Match': "Nosuch"})
        r = requests.get(url)
        resp = review_response(r, rules=_rules)

        self.assertEqual(resp.code, 200)
        self.assertEqual(resp.reason, None)

    @unittest.skip("Unimplemented")
    def test_malformed_headers(self, mockr):
        pass

    def test_page_content_present(self, mockr):
        url = "http://csirtfoundry.com"

        _rules = [{
            rules.NAME: "Test rule",
            rules.PRED: lambda r: rules_helpers.match_content(r, "Hello"),
            rules.RESULT_CODE: 500,
            rules.RESULT_REASON: "Hello string present",
        }]

        mockr.register_uri(
            'GET', url, text='Hello\nreturned')
        r = requests.get(url)
        resp = review_response(r, rules=_rules)

        self.assertEqual(resp.code, 500)
        self.assertEqual(resp.reason, "Hello string present")

    def test_page_content_present_unicode(self, mockr):
        url = "http://csirtfoundry.com"

        _rules = [{
            rules.NAME: "Test rule",
            rules.PRED: lambda r: rules_helpers.match_content(r, u"香港"),
            rules.RESULT_CODE: 404,
            rules.RESULT_REASON: "Missing in Hong Kong",
        }]

        mockr.register_uri(
            'GET', url, text=u'Hello香港\nreturned')
        logger.debug(u'香港')
        r = requests.get(url)
        logger.debug(r.encoding)
        logger.debug(u'%s' % r.text)
        logger.debug(u'{}'.format(r.text))
        resp = review_response(r, rules=_rules)

        self.assertEqual(resp.code, 404)
        self.assertEqual(resp.reason, "Missing in Hong Kong")

    def test_page_content_missing(self, mockr):
        url = "http://csirtfoundry.com"

        _rules = [{
            rules.NAME: "Test rule",
            rules.PRED: lambda r: rules_helpers.match_content(r, u"Not there"),
            rules.RESULT_CODE: 404,
            rules.RESULT_REASON: "Missing content?",
        }]

        mockr.register_uri(
            'GET', url, text='Hello\nreturned')
        r = requests.get(url)
        resp = review_response(r, rules=_rules)

        self.assertEqual(resp.code, 200)
        self.assertEqual(resp.reason, None)

    def test_multi_content_rule_match_get_first(self, mockr):
        url = "http://csirtfoundry.com"

        _rules = [
            {
                rules.NAME: "Content match",
                rules.PRED: lambda r: rules_helpers.match_content(r, u"Hello"),
                rules.RESULT_CODE: 404,
                rules.RESULT_REASON: "Hello rule",
            },
            {
                rules.NAME: "Header match",
                rules.PRED: lambda r: rules_helpers.match_header(r, "X-Match",
                                                                 "matched"),
                rules.RESULT_CODE: 500,
                rules.RESULT_REASON: "X-Match header",
            }
        ]

        mockr.register_uri(
            'GET', url, text='Hello\nreturned', headers={"X-Match": "matched"})
        r = requests.get(url)
        resp = review_response(r, rules=_rules)

        self.assertEqual(resp.code, 404)
        self.assertEqual(resp.reason, "Hello rule")

    def test_multi_content_boolean_test(self, mockr):
        url = "http://csirtfoundry.com"

        _rules = [
            {
                rules.NAME: "Content match",
                rules.PRED: lambda r: (
                    rules_helpers.match_content(r, u"Hello") and
                    rules_helpers.match_header(r, "X-match", "matched")
                ),
                rules.RESULT_CODE: 404,
                rules.RESULT_REASON: "Hello rule",
            },
        ]

        mockr.register_uri(
            'GET', url, text='Hello\nreturned', headers={"X-Match": "matched"})
        r = requests.get(url)
        resp = review_response(r, rules=_rules)

        self.assertEqual(resp.code, 404)
        self.assertEqual(resp.reason, "Hello rule")


@requests_mock.Mocker()
class TestRequests_reviewer_rulebase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_builtin_rules_have_all_keys(self, mockr):
        for rule in rules.rules:
            rule[rules.NAME]
            rule[rules.PRED]
            rule[rules.RESULT_CODE]
            rule[rules.RESULT_REASON]

    def test_suspended_page_cgi(self, mockr):
        url = "http://csirtfoundry.com"

        mockr.register_uri(
            'GET', url, text='Hello\nreturned',
            headers={"Location": "http://example.com/suspendedpage.cgi"})
        r = requests.get(url)
        resp = review_response(r)

        self.assertEqual(resp.code, 403)
        self.assertEqual(resp.reason, "Common suspension URL")


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
