import unittest
import mock
import koalaoauth2
from datetime import datetime
from oauthlib.common import Request
from google.appengine.ext import testbed
from google.appengine.ext import deferred
from google.appengine.ext import ndb

__author__ = 'Matt'


class TestClient(unittest.TestCase):
    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_search_stub()
        self.testbed.init_taskqueue_stub(root_path='.')
        self.task_queue = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)
        # Remaining setup needed for test cases

        # You need to be careful with the client_id param. It will be used exactly as is, and it is used as the key
        # for the datastore
        self.test_client_with_spaces = {
            'guid': '  guid  ',
            'redirect_uris': '  http://localhost:8080  ',
            'client_type': koalaoauth2.CLIENT_PUBLIC,
            'authorization_grant_type': koalaoauth2.GRANT_PASSWORD,
            'client_id': 'client_id',
            'client_secret': '  client_secret  ',
            'client_name': '  name',
            'skip_authorization': False,
        }
        self.test_client = {
            'guid': 'guid',
            'redirect_uris': 'http://localhost:8080',
            'client_type': koalaoauth2.CLIENT_PUBLIC,
            'authorization_grant_type': koalaoauth2.GRANT_PASSWORD,
            'client_id': 'client_id',
            'client_secret': 'client_secret',
            'client_name': 'name',
            'skip_authorization': False,
        }

    def tearDown(self):
        self.testbed.deactivate()

    def test_insert_client(self):
        client = koalaoauth2.Clients.new(**self.test_client)
        client_uid = koalaoauth2.Clients.insert(resource_object=client)
        self.assertTrue(client_uid)

    def test_get_client(self):
        client = koalaoauth2.Clients.new(**self.test_client)
        koalaoauth2.Clients.insert(resource_object=client)

        retrieved_client = koalaoauth2.Clients.get(resource_uid=client.client_id)
        self.assertTrue(retrieved_client, u'Stored value mismatch')
        self.assertTrue(retrieved_client.uid, u'Stored value mismatch')
        self.assertTrue(isinstance(retrieved_client.created, datetime), u'Stored value mismatch')
        self.assertTrue(isinstance(retrieved_client.updated, datetime), u'Stored value mismatch')
        self.assertEqual(retrieved_client.guid, self.test_client['guid'], u'Stored guid value mismatch')
        self.assertEqual(retrieved_client.redirect_uris, self.test_client['redirect_uris'], u'Stored redirect_uris value mismatch')
        self.assertEqual(retrieved_client.client_type, self.test_client['client_type'], u'Stored client_type value mismatch')
        self.assertEqual(retrieved_client.authorization_grant_type, self.test_client['authorization_grant_type'], u'Stored authorization_grant_type value mismatch')
        self.assertEqual(retrieved_client.client_id, self.test_client['client_id'], u'Stored client_id value mismatch')
        self.assertEqual(retrieved_client.client_secret, self.test_client['client_secret'], u'Stored client_secret value mismatch')
        self.assertEqual(retrieved_client.client_name, self.test_client['client_name'], u'Stored name value mismatch')
        self.assertEqual(retrieved_client.skip_authorization, self.test_client['skip_authorization'], u'Stored skip_authorization value mismatch')

    def test_insert_client_strip_filter(self):
        client = koalaoauth2.Clients.new(**self.test_client_with_spaces)
        inserted_uid = koalaoauth2.Clients.insert(resource_object=client)

        retrieved_client = koalaoauth2.Clients.get(resource_uid=client.client_id)

        self.assertEqual(retrieved_client.guid, self.test_client['guid'], u'Stored guid value mismatch')
        self.assertEqual(retrieved_client.redirect_uris, self.test_client['redirect_uris'], u'Stored redirect_uris value mismatch')
        self.assertEqual(retrieved_client.client_type, self.test_client['client_type'], u'Stored client_type value mismatch')
        self.assertEqual(retrieved_client.authorization_grant_type, self.test_client['authorization_grant_type'], u'Stored authorization_grant_type value mismatch')
        self.assertEqual(retrieved_client.client_id, self.test_client['client_id'], u'Stored client_id value mismatch')
        self.assertEqual(retrieved_client.client_secret, self.test_client['client_secret'], u'Stored client_secret value mismatch')
        self.assertEqual(retrieved_client.client_name, self.test_client['client_name'], u'Stored name value mismatch')
        self.assertEqual(retrieved_client.skip_authorization, self.test_client['skip_authorization'], u'Stored skip_authorization value mismatch')

    def test_update_client(self):
        client = koalaoauth2.Clients.new(**self.test_client)
        koalaoauth2.Clients.insert(resource_object=client)
        retrieved_client = koalaoauth2.Clients.get(resource_uid=client.client_id)

        # Client ID and Client Secret should never change. If you find that you need to edit one then you need to delete
        # the existing client and recreate it.

        retrieved_client.guid = 'updated_guid'
        retrieved_client.redirect_uris = 'http://localhost:6060'
        retrieved_client.client_type = koalaoauth2.CLIENT_CONFIDENTIAL
        retrieved_client.authorization_grant_type = koalaoauth2.GRANT_AUTHORIZATION_CODE
        retrieved_client.client_name = 'updated_name'
        retrieved_client.skip_authorization = True

        koalaoauth2.Clients.update(resource_object=retrieved_client)
        updated_client = koalaoauth2.Clients.get(resource_uid=client.client_id)

        # TODO: fix this in the API and re-implement the correct test
        # self.assertEqual(retrieved_client.uid, updated_client.uid, u'UID mismatch')
        self.assertEqual(retrieved_client.client_id, updated_client.uid, u'UID mismatch')
        self.assertEqual(retrieved_client.created, updated_client.created, u'Created date has changed')
        self.assertNotEqual(retrieved_client.updated, updated_client.updated, u'Updated date not changed')
        self.assertEqual(updated_client.guid, 'updated_guid', u'Stored guid value mismatch')
        self.assertEqual(updated_client.redirect_uris, 'http://localhost:6060', u'Stored redirect_uris value mismatch')
        self.assertEqual(updated_client.client_type, koalaoauth2.CLIENT_CONFIDENTIAL, u'Stored client_type value mismatch')
        self.assertEqual(updated_client.authorization_grant_type, koalaoauth2.GRANT_AUTHORIZATION_CODE, u'Stored authorization_grant_type value mismatch')
        self.assertEqual(updated_client.client_name, 'updated_name', u'Stored name value mismatch')
        self.assertEqual(updated_client.skip_authorization, True, u'Stored skip_authorization value mismatch')

    def test_delete_client(self):
        client = koalaoauth2.Clients.new(**self.test_client)
        koalaoauth2.Clients.insert(resource_object=client)
        koalaoauth2.Clients.delete(resource_uid=client.client_id)
        retrieved_client = koalaoauth2.Clients.get(resource_uid=client.client_id)
        self.assertFalse(retrieved_client)

    def test_insert_search(self):
        client = koalaoauth2.Clients.new(**self.test_client)
        koalaoauth2.Clients.insert(resource_object=client)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 1, u'Deferred task missing')

        deferred.run(tasks[0].payload)  # Doesn't return anything so nothing to test

        search_result = koalaoauth2.Clients.search(
            query_string='client_name: {}'.format(self.test_client['client_name']))
        self.assertEqual(search_result.results_count, 1, u'Query returned incorrect count')
        self.assertEqual(len(search_result.results), 1, u'Query returned incorrect number of results')

    def test_update_search(self):
        client = koalaoauth2.Clients.new(**self.test_client)
        koalaoauth2.Clients.insert(resource_object=client)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 1, u'Invalid number of Deferred tasks')

        deferred.run(tasks[0].payload)  # Doesn't return anything so nothing to test

        retrieved_client = koalaoauth2.Clients.get(resource_uid=client.client_id)
        retrieved_client.client_name = 'updated_client_name'
        koalaoauth2.Clients.update(resource_object=retrieved_client)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 2, u'Invalid number of Deferred tasks')

        deferred.run(tasks[1].payload)  # Doesn't return anything so nothing to test

        search_result = koalaoauth2.Clients.search(query_string='client_name: {}'.format('updated_client_name'))
        self.assertEqual(search_result.results_count, 1, u'Query returned incorrect count')
        self.assertEqual(len(search_result.results), 1, u'Query returned incorrect number of results')

    def test_delete_search(self):
        client = koalaoauth2.Clients.new(**self.test_client)
        koalaoauth2.Clients.insert(resource_object=client)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 1, u'Invalid number of Deferred tasks')

        deferred.run(tasks[0].payload)  # Doesn't return anything so nothing to test

        koalaoauth2.Clients.delete(resource_uid=client.client_id)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 2, u'Invalid number of Deferred tasks')

        deferred.run(tasks[1].payload)  # Doesn't return anything so nothing to test

        search_result = koalaoauth2.Clients.search(
            query_string='client_name: {}'.format(self.test_client['client_name']))
        self.assertEqual(search_result.results_count, 0, u'Query returned incorrect count')
        self.assertEqual(len(search_result.results), 0, u'Query returned incorrect number of results')

    def test_auto_generated_client_id_and_secret(self):
        # TODO: test that not passing client_id and/or client_secret will autogenerate values
        pass


class TestAccessToken(unittest.TestCase):
    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_search_stub()
        self.testbed.init_taskqueue_stub(root_path='.')
        self.task_queue = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)
        # Remaining setup needed for test cases
        test_expires = datetime.now()

        # You need to be careful with the token param. It will be used exactly as is, and it is used as the key
        # for the datastore
        self.test_access_token_with_spaces = {
            'guid': '  guid  ',
            'token': 'token',
            'client_id': '  client_id  ',
            'expires': test_expires,
            'scope': '  scope  ',
        }
        self.test_access_token = {
            'guid': 'guid',
            'token': 'token',
            'client_id': 'client_id',
            'expires': test_expires,
            'scope': 'scope',
        }

    def tearDown(self):
        self.testbed.deactivate()

    def test_insert_access_token(self):
        access_token = koalaoauth2.AccessTokens.new(**self.test_access_token)
        access_token_uid = koalaoauth2.AccessTokens.insert(resource_object=access_token)
        self.assertTrue(access_token_uid)

    def test_get_access_token(self):
        access_token = koalaoauth2.AccessTokens.new(**self.test_access_token)
        koalaoauth2.AccessTokens.insert(resource_object=access_token)

        retrieved_access_token = koalaoauth2.AccessTokens.get(resource_uid=access_token.token)
        self.assertTrue(retrieved_access_token, u'Stored value mismatch')
        self.assertTrue(retrieved_access_token.uid, u'Stored value mismatch')
        self.assertTrue(isinstance(retrieved_access_token.created, datetime), u'Stored value mismatch')
        self.assertTrue(isinstance(retrieved_access_token.updated, datetime), u'Stored value mismatch')
        self.assertEqual(retrieved_access_token.guid, self.test_access_token['guid'], u'Stored guid value mismatch')
        self.assertEqual(retrieved_access_token.client_id, self.test_access_token['client_id'], u'Stored access_token_id value mismatch')
        self.assertEqual(retrieved_access_token.token, self.test_access_token['token'], u'Stored token value mismatch')
        self.assertEqual(retrieved_access_token.expires, self.test_access_token['expires'], u'Stored expires value mismatch')
        self.assertEqual(retrieved_access_token.scope, self.test_access_token['scope'], u'Stored scope value mismatch')

    def test_insert_access_token_strip_filter(self):
        access_token = koalaoauth2.AccessTokens.new(**self.test_access_token_with_spaces)
        inserted_uid = koalaoauth2.AccessTokens.insert(resource_object=access_token)

        retrieved_access_token = koalaoauth2.AccessTokens.get(resource_uid=access_token.token)

        self.assertEqual(retrieved_access_token.guid, self.test_access_token['guid'], u'Stored guid value mismatch')
        self.assertEqual(retrieved_access_token.client_id, self.test_access_token['client_id'], u'Stored access_token_id value mismatch')
        self.assertEqual(retrieved_access_token.token, self.test_access_token['token'], u'Stored token value mismatch')
        self.assertEqual(retrieved_access_token.expires, self.test_access_token['expires'], u'Stored expires value mismatch')
        self.assertEqual(retrieved_access_token.scope, self.test_access_token['scope'], u'Stored scope value mismatch')

    def test_delete_access_token(self):
        access_token = koalaoauth2.AccessTokens.new(**self.test_access_token)
        koalaoauth2.AccessTokens.insert(resource_object=access_token)
        koalaoauth2.AccessTokens.delete(resource_uid=access_token.token)
        retrieved_access_token = koalaoauth2.AccessTokens.get(resource_uid=access_token.token)
        self.assertFalse(retrieved_access_token)

    def test_insert_search(self):
        access_token = koalaoauth2.AccessTokens.new(**self.test_access_token)
        koalaoauth2.AccessTokens.insert(resource_object=access_token)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 1, u'Deferred task missing')

        deferred.run(tasks[0].payload)  # Doesn't return anything so nothing to test

        search_result = koalaoauth2.AccessTokens.search(
            query_string='token: {}'.format(self.test_access_token['token']))
        self.assertEqual(search_result.results_count, 1, u'Query returned incorrect count')
        self.assertEqual(len(search_result.results), 1, u'Query returned incorrect number of results')

    def test_delete_search(self):
        access_token = koalaoauth2.AccessTokens.new(**self.test_access_token)
        inserted_uid = koalaoauth2.AccessTokens.insert(resource_object=access_token)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 1, u'Invalid number of Deferred tasks')

        deferred.run(tasks[0].payload)  # Doesn't return anything so nothing to test

        koalaoauth2.AccessTokens.delete(resource_uid=access_token.token)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 2, u'Invalid number of Deferred tasks')

        deferred.run(tasks[1].payload)  # Doesn't return anything so nothing to test

        search_result = koalaoauth2.AccessTokens.search(
            query_string='token: {}'.format(self.test_access_token['token']))
        self.assertEqual(search_result.results_count, 0, u'Query returned incorrect count')
        self.assertEqual(len(search_result.results), 0, u'Query returned incorrect number of results')


class TestRefreshToken(unittest.TestCase):
    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_search_stub()
        self.testbed.init_taskqueue_stub(root_path='.')
        self.task_queue = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)
        # Remaining setup needed for test cases

        # You need to be careful with the token param. It will be used exactly as is, and it is used as the key
        # for the datastore
        self.test_refresh_token_with_spaces = {
            'guid': 'guid',
            'token': 'token',
            'client_id': 'client_id',
            'access_token': 'access_token',
        }
        self.test_refresh_token = {
            'guid': 'guid',
            'token': 'token',
            'client_id': 'client_id',
            'access_token': 'access_token',
        }

    def tearDown(self):
        self.testbed.deactivate()

    def test_insert_refresh_token(self):
        refresh_token = koalaoauth2.RefreshTokens.new(**self.test_refresh_token)
        refresh_token_uid = koalaoauth2.RefreshTokens.insert(resource_object=refresh_token)
        self.assertTrue(refresh_token_uid)

    def test_get_refresh_token(self):
        refresh_token = koalaoauth2.RefreshTokens.new(**self.test_refresh_token)
        koalaoauth2.RefreshTokens.insert(resource_object=refresh_token)

        retrieved_refresh_token = koalaoauth2.RefreshTokens.get(resource_uid=refresh_token.token)
        self.assertTrue(retrieved_refresh_token, u'Stored value mismatch')
        self.assertTrue(retrieved_refresh_token.uid, u'Stored value mismatch')
        self.assertTrue(isinstance(retrieved_refresh_token.created, datetime), u'Stored value mismatch')
        self.assertTrue(isinstance(retrieved_refresh_token.updated, datetime), u'Stored value mismatch')
        self.assertEqual(retrieved_refresh_token.guid, self.test_refresh_token['guid'], u'Stored guid value mismatch')
        self.assertEqual(retrieved_refresh_token.client_id, self.test_refresh_token['client_id'], u'Stored refresh_token_id value mismatch')
        self.assertEqual(retrieved_refresh_token.token, self.test_refresh_token['token'], u'Stored token value mismatch')
        self.assertEqual(retrieved_refresh_token.access_token, self.test_refresh_token['access_token'], u'Stored access_token value mismatch')

    def test_insert_refresh_token_strip_filter(self):
        refresh_token = koalaoauth2.RefreshTokens.new(**self.test_refresh_token_with_spaces)
        inserted_uid = koalaoauth2.RefreshTokens.insert(resource_object=refresh_token)

        retrieved_refresh_token = koalaoauth2.RefreshTokens.get(resource_uid=refresh_token.token)

        self.assertEqual(retrieved_refresh_token.guid, self.test_refresh_token['guid'], u'Stored guid value mismatch')
        self.assertEqual(retrieved_refresh_token.client_id, self.test_refresh_token['client_id'], u'Stored refresh_token_id value mismatch')
        self.assertEqual(retrieved_refresh_token.token, self.test_refresh_token['token'], u'Stored token value mismatch')
        self.assertEqual(retrieved_refresh_token.access_token, self.test_refresh_token['access_token'], u'Stored access_token value mismatch')

    def test_delete_refresh_token(self):
        refresh_token = koalaoauth2.RefreshTokens.new(**self.test_refresh_token)
        koalaoauth2.RefreshTokens.insert(resource_object=refresh_token)
        koalaoauth2.RefreshTokens.delete(resource_uid=refresh_token.token)
        retrieved_refresh_token = koalaoauth2.RefreshTokens.get(resource_uid=refresh_token.token)
        self.assertFalse(retrieved_refresh_token)

    def test_insert_search(self):
        refresh_token = koalaoauth2.RefreshTokens.new(**self.test_refresh_token)
        koalaoauth2.RefreshTokens.insert(resource_object=refresh_token)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 1, u'Deferred task missing')

        deferred.run(tasks[0].payload)  # Doesn't return anything so nothing to test

        search_result = koalaoauth2.RefreshTokens.search(
            query_string='token: {}'.format(self.test_refresh_token['token']))
        self.assertEqual(search_result.results_count, 1, u'Query returned incorrect count')
        self.assertEqual(len(search_result.results), 1, u'Query returned incorrect number of results')

    def test_delete_search(self):
        refresh_token = koalaoauth2.RefreshTokens.new(**self.test_refresh_token)
        koalaoauth2.RefreshTokens.insert(resource_object=refresh_token)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 1, u'Invalid number of Deferred tasks')

        deferred.run(tasks[0].payload)  # Doesn't return anything so nothing to test

        koalaoauth2.RefreshTokens.delete(resource_uid=refresh_token.token)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 2, u'Invalid number of Deferred tasks')

        deferred.run(tasks[1].payload)  # Doesn't return anything so nothing to test

        search_result = koalaoauth2.RefreshTokens.search(
            query_string='token: {}'.format(self.test_refresh_token['token']))
        self.assertEqual(search_result.results_count, 0, u'Query returned incorrect count')
        self.assertEqual(len(search_result.results), 0, u'Query returned incorrect number of results')


class TestGrant(unittest.TestCase):
    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_search_stub()
        self.testbed.init_taskqueue_stub(root_path='.')
        self.task_queue = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)
        # Remaining setup needed for test cases
        test_expires = datetime.now()
        # You need to be careful with the client_id param. It will be used exactly as is, and it is used as the key
        # for the datastore
        self.test_grant_with_spaces = {
            'guid': '  guid  ',
            'redirect_uri': '  http://localhost:8080  ',
            'code': 'code',
            'client_id': 'client_id',
            'expires': test_expires,
            'scope': 'scope',
        }
        self.test_grant = {
            'guid': 'guid',
            'redirect_uri': 'http://localhost:8080',
            'code': 'code',
            'client_id': 'client_id',
            'expires': test_expires,
            'scope': 'scope',
        }

    def tearDown(self):
        self.testbed.deactivate()

    def test_insert_grant(self):
        grant = koalaoauth2.Grants.new(**self.test_grant)
        grant_uid = koalaoauth2.Grants.insert(resource_object=grant)
        self.assertTrue(grant_uid)

    def test_get_grant(self):
        grant = koalaoauth2.Grants.new(**self.test_grant)
        inserted_uid = koalaoauth2.Grants.insert(resource_object=grant)

        retrieved_grant = koalaoauth2.Grants.get(resource_uid=inserted_uid)
        self.assertTrue(retrieved_grant, u'Stored value mismatch')
        self.assertTrue(retrieved_grant.uid, u'Stored value mismatch')
        self.assertTrue(isinstance(retrieved_grant.created, datetime), u'Stored value mismatch')
        self.assertTrue(isinstance(retrieved_grant.updated, datetime), u'Stored value mismatch')
        self.assertEqual(retrieved_grant.guid, self.test_grant['guid'], u'Stored guid value mismatch')
        self.assertEqual(retrieved_grant.redirect_uri, self.test_grant['redirect_uri'], u'Stored redirect_uri value mismatch')
        self.assertEqual(retrieved_grant.code, self.test_grant['code'], u'Stored code value mismatch')
        self.assertEqual(retrieved_grant.client_id, self.test_grant['client_id'], u'Stored client_id value mismatch')
        self.assertEqual(retrieved_grant.expires, self.test_grant['expires'], u'Stored expires value mismatch')
        self.assertEqual(retrieved_grant.scope, self.test_grant['scope'], u'Stored scope value mismatch')

    def test_insert_grant_strip_filter(self):
        grant = koalaoauth2.Grants.new(**self.test_grant_with_spaces)
        inserted_uid = koalaoauth2.Grants.insert(resource_object=grant)

        retrieved_grant = koalaoauth2.Grants.get(resource_uid=inserted_uid)

        self.assertEqual(retrieved_grant.guid, self.test_grant['guid'], u'Stored guid value mismatch')
        self.assertEqual(retrieved_grant.redirect_uri, self.test_grant['redirect_uri'], u'Stored redirect_uri value mismatch')
        self.assertEqual(retrieved_grant.code, self.test_grant['code'], u'Stored code value mismatch')
        self.assertEqual(retrieved_grant.client_id, self.test_grant['client_id'], u'Stored client_id value mismatch')
        self.assertEqual(retrieved_grant.expires, self.test_grant['expires'], u'Stored expires value mismatch')
        self.assertEqual(retrieved_grant.scope, self.test_grant['scope'], u'Stored scope value mismatch')

    def test_update_grant(self):
        grant = koalaoauth2.Grants.new(**self.test_grant)
        inserted_uid = koalaoauth2.Grants.insert(resource_object=grant)
        retrieved_grant = koalaoauth2.Grants.get(resource_uid=inserted_uid)

        updated_expires = datetime.now()

        retrieved_grant.guid = 'updated_guid'
        retrieved_grant.redirect_uri = 'updated_redirect_uri'
        retrieved_grant.code = 'updated_code'
        retrieved_grant.client_id = 'updated_client_id'
        retrieved_grant.expires = updated_expires
        retrieved_grant.scope = 'updated_scope'

        koalaoauth2.Grants.update(resource_object=retrieved_grant)
        updated_grant = koalaoauth2.Grants.get(resource_uid=inserted_uid)

        self.assertEqual(retrieved_grant.uid, updated_grant.uid, u'UID mismatch')
        self.assertEqual(retrieved_grant.created, updated_grant.created, u'Created date has changed')
        self.assertNotEqual(retrieved_grant.updated, updated_grant.updated, u'Updated date not changed')
        self.assertEqual(updated_grant.guid, 'updated_guid', u'Stored guid value mismatch')
        self.assertEqual(updated_grant.redirect_uri, 'updated_redirect_uri', u'Stored redirect_uri value mismatch')
        self.assertEqual(updated_grant.code, 'updated_code', u'Stored code value mismatch')
        self.assertEqual(updated_grant.client_id, 'updated_client_id', u'Stored client_id value mismatch')
        self.assertEqual(updated_grant.expires, updated_expires, u'Stored expires value mismatch')
        self.assertEqual(updated_grant.scope, 'updated_scope', u'Stored scope value mismatch')

    def test_delete_grant(self):
        grant = koalaoauth2.Grants.new(**self.test_grant)
        inserted_uid = koalaoauth2.Grants.insert(resource_object=grant)
        koalaoauth2.Grants.delete(resource_uid=inserted_uid)
        retrieved_grant = koalaoauth2.Grants.get(resource_uid=inserted_uid)
        self.assertFalse(retrieved_grant)

    def test_insert_search(self):
        grant = koalaoauth2.Grants.new(**self.test_grant)
        inserted_uid = koalaoauth2.Grants.insert(resource_object=grant)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 1, u'Deferred task missing')

        deferred.run(tasks[0].payload)  # Doesn't return anything so nothing to test

        search_result = koalaoauth2.Grants.search(
            query_string='code: {}'.format(self.test_grant['code']))
        self.assertEqual(search_result.results_count, 1, u'Query returned incorrect count')
        self.assertEqual(len(search_result.results), 1, u'Query returned incorrect number of results')

    def test_update_search(self):
        grant = koalaoauth2.Grants.new(**self.test_grant)
        inserted_uid = koalaoauth2.Grants.insert(resource_object=grant)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 1, u'Invalid number of Deferred tasks')

        deferred.run(tasks[0].payload)  # Doesn't return anything so nothing to test

        retrieved_grant = koalaoauth2.Grants.get(resource_uid=inserted_uid)
        retrieved_grant.code = 'updated_code'
        koalaoauth2.Grants.update(resource_object=retrieved_grant)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 2, u'Invalid number of Deferred tasks')

        deferred.run(tasks[1].payload)  # Doesn't return anything so nothing to test

        search_result = koalaoauth2.Grants.search(query_string='code: {}'.format('updated_code'))
        self.assertEqual(search_result.results_count, 1, u'Query returned incorrect count')
        self.assertEqual(len(search_result.results), 1, u'Query returned incorrect number of results')

    def test_delete_search(self):
        grant = koalaoauth2.Grants.new(**self.test_grant)
        inserted_uid = koalaoauth2.Grants.insert(resource_object=grant)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 1, u'Invalid number of Deferred tasks')

        deferred.run(tasks[0].payload)  # Doesn't return anything so nothing to test

        koalaoauth2.Grants.delete(resource_uid=inserted_uid)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 2, u'Invalid number of Deferred tasks')

        deferred.run(tasks[1].payload)  # Doesn't return anything so nothing to test

        search_result = koalaoauth2.Grants.search(
            query_string='code: {}'.format(self.test_grant['code']))
        self.assertEqual(search_result.results_count, 0, u'Query returned incorrect count')
        self.assertEqual(len(search_result.results), 0, u'Query returned incorrect number of results')


class TestOAuth2Validator(unittest.TestCase):
    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_search_stub()
        self.testbed.init_taskqueue_stub(root_path='.')
        self.task_queue = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)
        # Remaining setup needed for test cases
        self.request = mock.MagicMock(wraps=Request)
        self.request.client = None
        self.validator = koalaoauth2.OAuth2RequestValidator()
        client = koalaoauth2.Clients.new(client_id='client_id',
                                         client_secret='client_secret',
                                         guid='test_user_guid',
                                         client_type=koalaoauth2.CLIENT_PUBLIC,
                                         authorization_grant_type=koalaoauth2.GRANT_PASSWORD)
        koalaoauth2.Clients.insert(resource_object=client)
        self.client = client

    def tearDown(self):
        koalaoauth2.Clients.delete(resource_uid=self.client.client_id)
        self.testbed.deactivate()

    def test_authenticate_request_body(self):
        self.request.client_id = 'client_id'
        self.request.client_secret = ''
        self.assertFalse(self.validator._authenticate_request_body(self.request))

        self.request.client_secret = 'wrong_client_secret'
        self.assertFalse(self.validator._authenticate_request_body(self.request))

        self.request.client_secret = 'client_secret'
        self.assertTrue(self.validator._authenticate_request_body(self.request))

    def test_extract_basic_auth(self):
        self.request.headers = {'HTTP_AUTHORIZATION': 'Basic 123456'}
        self.assertEqual(self.validator._extract_basic_auth(self.request), '123456')
        self.request.headers = {}
        self.assertIsNone(self.validator._extract_basic_auth(self.request))
        self.request.headers = {'HTTP_AUTHORIZATION': 'Dummy 123456'}
        self.assertIsNone(self.validator._extract_basic_auth(self.request))
        self.request.headers = {'HTTP_AUTHORIZATION': 'Basic'}
        self.assertIsNone(self.validator._extract_basic_auth(self.request))
        self.request.headers = {'HTTP_AUTHORIZATION': 'Basic 123456 789'}
        self.assertEqual(self.validator._extract_basic_auth(self.request), '123456 789')

    def test_authenticate_basic_auth(self):
        self.request.encoding = 'utf-8'
        # client_id:client_secret
        self.request.headers = {'HTTP_AUTHORIZATION': 'Basic Y2xpZW50X2lkOmNsaWVudF9zZWNyZXQ=\n'}
        self.assertTrue(self.validator._authenticate_basic_auth(self.request))

    def test_authenticate_basic_auth_wrong_client_id(self):
        self.request.encoding = 'utf-8'
        # wrong_id:client_secret
        self.request.headers = {'HTTP_AUTHORIZATION': 'Basic d3JvbmdfaWQ6Y2xpZW50X3NlY3JldA==\n'}
        self.assertFalse(self.validator._authenticate_basic_auth(self.request))

    def test_authenticate_basic_auth_wrong_client_secret(self):
        self.request.encoding = 'utf-8'
        # client_id:wrong_secret
        self.request.headers = {'HTTP_AUTHORIZATION': 'Basic Y2xpZW50X2lkOndyb25nX3NlY3JldA==\n'}
        self.assertFalse(self.validator._authenticate_basic_auth(self.request))

    def test_authenticate_basic_auth_not_b64_auth_string(self):
        self.request.encoding = 'utf-8'
        # Can't b64decode
        self.request.headers = {'HTTP_AUTHORIZATION': 'Basic not_base64'}
        self.assertFalse(self.validator._authenticate_basic_auth(self.request))

    def test_authenticate_basic_auth_not_utf8(self):
        self.request.encoding = 'utf-8'
        # b64decode('test') will become b'\xb5\xeb-', it can't be decoded as utf-8
        self.request.headers = {'HTTP_AUTHORIZATION': 'Basic test'}
        self.assertFalse(self.validator._authenticate_basic_auth(self.request))

    def test_authenticate_client_id(self):
        self.assertTrue(self.validator.authenticate_client_id('client_id', self.request))

    def test_authenticate_client_id_fail(self):
        self.client.client_type = koalaoauth2.CLIENT_CONFIDENTIAL
        koalaoauth2.Clients.update(resource_object=self.client)
        self.assertFalse(self.validator.authenticate_client_id('client_id', self.request))
        self.assertFalse(self.validator.authenticate_client_id('fake_client_id', self.request))

    def test_client_authentication_required(self):
        self.request.headers = {'HTTP_AUTHORIZATION': 'Basic 123456'}
        self.assertTrue(self.validator.client_authentication_required(self.request))
        self.request.headers = {}
        self.request.client_id = 'client_id'
        self.request.client_secret = 'client_secret'
        self.assertTrue(self.validator.client_authentication_required(self.request))
        self.request.client_secret = ''
        self.assertFalse(self.validator.client_authentication_required(self.request))
        self.client.client_type = koalaoauth2.CLIENT_CONFIDENTIAL
        koalaoauth2.Clients.update(resource_object=self.client)
        self.request.client = ''
        self.assertTrue(self.validator.client_authentication_required(self.request))

    def test_load_application_fails_when_request_has_no_client(self):
        self.assertRaises(AssertionError, self.validator.authenticate_client_id, 'client_id', {})
