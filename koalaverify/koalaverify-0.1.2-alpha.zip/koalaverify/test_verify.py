import unittest
from google.appengine.ext import testbed
import koalaverify

__author__ = 'Matt'


class TestVerifyToken(unittest.TestCase):
    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        # Remaining setup needed for test cases

    def tearDown(self):
        self.testbed.deactivate()

    def test_generate_token(self):
        token = koalaverify.Verification.generate(token_uid='test_user_id', redirect_uri='test.route.id')
        self.assertTrue(token)

    def test_verify_token_only(self):
        token = koalaverify.Verification.generate(token_uid='test_user_id', redirect_uri='test.route.id')
        self.assertTrue(koalaverify.Verification.verify(token=token))

    def test_verify_token_with_uid(self):
        token = koalaverify.Verification.generate(token_uid='test_user_id', redirect_uri='test.route.id')
        self.assertTrue(koalaverify.Verification.verify(token=token, token_uid='test_user_id'))

    def test_verify_token_with_uid_and_redirect_uri(self):
        token = koalaverify.Verification.generate(token_uid='test_user_id', redirect_uri='test.route.id')
        self.assertTrue(koalaverify.Verification.verify(token=token, token_uid='test_user_id', redirect_uri='test.route.id'))

    def test_verify_token_with_invalid_uid(self):
        token = koalaverify.Verification.generate(token_uid='test_user_id', redirect_uri='test.route.id')
        valid, message = koalaverify.Verification.verify(token=token, token_uid='invalid_uid')
        self.assertFalse(valid)

    def test_verify_token_with_invalid_redirect_uri(self):
        token = koalaverify.Verification.generate(token_uid='test_user_id', redirect_uri='test.route.id')
        valid, message = koalaverify.Verification.verify(token=token, redirect_uri='invalid.route.id')
        self.assertFalse(valid)

    def test_valid_once(self):
        token = koalaverify.Verification.generate(token_uid='test_user_id', redirect_uri='test.route.id')
        self.assertTrue(koalaverify.Verification.verify(token=token))
        valid, message = koalaverify.Verification.verify(token=token)
        self.assertFalse(valid)

