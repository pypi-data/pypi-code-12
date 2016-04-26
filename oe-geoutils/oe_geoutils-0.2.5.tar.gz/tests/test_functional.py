# -*- coding: utf-8 -*-
import os
import unittest
import json

from paste.deploy import appconfig
from webtest import TestApp
from pyramid import testing

try:
    from testdata import test_json_outside_flanders, test_json_intersects_flanders
except:
    from tests.testdata import test_json_outside_flanders, test_json_intersects_flanders
from oe_geoutils import main

from oe_geoutils.views.exceptions import internal_server_error

here = os.path.dirname(__file__)

test_geom = json.dumps({
            "type": "MultiPolygon",
            "coordinates": [[[[172933.6922879719058983, 174851.14960918109863997],
                              [172930.21180502674542367, 174832.7836931711062789],
                              [172920.64762709615752101, 174848.13247794657945633],
                              [172933.6922879719058983, 174851.14960918109863997]]]],
            "crs": {
                "type": "name",
                "properties": {
                    "name": "urn:ogc:def:crs:EPSG::31370"
                }
            }
        })


class FunctionalTests(unittest.TestCase):
    def _get_default_headers(self):
        return {'Accept': 'application/json'}

    @classmethod
    def setUpClass(cls):
        cls.settings = appconfig('config:' + os.path.join(here, 'test.ini'))

    def setUp(self):
        self.app = main({}, **self.settings)
        self.testapp = TestApp(self.app)

    def tearDown(self):
        self.testapp.reset()

    def test_get_nearest_address(self):
        res = self.testapp.post('/nearest_address', test_geom)
        self.assertEqual('200 OK', res.status)

    def test_get_nearest_address_outside_Flanders(self):
        res = self.testapp.post('/nearest_address', json.dumps(test_json_outside_flanders), expect_errors=True)
        self.assertEqual('400 Bad Request', res.status)

    def test_get_nearest_address_not_found(self):
        res = self.testapp.post('/nearest_address', json.dumps(test_json_intersects_flanders), expect_errors=True)
        self.assertEqual('200 OK', res.status)

    def test_check_in_flanders(self):
        res = self.testapp.post('/check_in_flanders', test_geom)
        self.assertEqual('200 OK', res.status)

    def test_check_within_flanders(self):
        res = self.testapp.post('/check_within_flanders', test_geom)
        self.assertEqual('200 OK', res.status)

    def test_check_in_flanders_no_json_body(self):
        res = self.testapp.post('/check_in_flanders', expect_errors=True)
        self.assertEqual('400 Bad Request', res.status)

    def test_check_in_flanders_validation_failure(self):
        res = self.testapp.post('/check_in_flanders', '{}', expect_errors=True)
        self.assertEqual('400 Bad Request', res.status)

    def test_check_in_flanders_invalid_url(self):
        res = self.testapp.post('/test', '{}', expect_errors=True)
        self.assertEqual('404 Not Found', res.status)

    def test_internal_server_error(self):
        a = Exception()
        internal_server_error(a, testing.DummyRequest())


