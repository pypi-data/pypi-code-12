import unittest
import koalacore
import koalausers
import google.appengine.ext.ndb as ndb
from google.appengine.ext import testbed
from google.appengine.ext import deferred
from datetime import datetime


__author__ = 'Matt'


class TestUserResource(unittest.TestCase):
    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        # Remaining setup needed for test cases

    def tearDown(self):
        self.testbed.deactivate()

    def test_user_modified_flags(self):
        user = koalausers.Users.new(username='test', email_address='foss@lighthouseuk.net', first_name='Test', raw_password='test', last_name='User', language_preference='en')
        self.assertFalse('username' in user._uniques_modified, u'Modified flag set')
        self.assertFalse('email_address' in user._uniques_modified, u'Modified flag set')
        self.assertFalse('recovery_email_address' in user._uniques_modified, u'Modified flag set')
        user.username = 'test_modified'
        user.email_address = 'matt+modified@lighthouseuk.net'
        user.recovery_email_address = 'matt+recovery@lighthouseuk.net'
        self.assertTrue('username' in user._uniques_modified, u'Modified not flag set')
        self.assertTrue('email_address' in user._uniques_modified, u'Modified not flag set')
        self.assertTrue('recovery_email_address' in user._uniques_modified, u'Modified not flag set')

    def test_user_auth_ids(self):
        user = koalausers.Users.new(username='test', email_address='foss@lighthouseuk.net', first_name='Test', raw_password='test', last_name='User', language_preference='en')
        self.assertEqual(user.auth_ids, ['test', 'foss@lighthouseuk.net'], u'User auth_ids mismatch')

    def test_user_change_password(self):
        user = koalausers.Users.new(username='test', email_address='foss@lighthouseuk.net', first_name='Test', raw_password='test', last_name='User', language_preference='en')
        internal_dict = user.as_dict()
        user.change_password(raw_password='modified_password')
        self.assertNotEqual(internal_dict['password'], user.password, u'Changed password value matches existing')

    def test_user_property_titles(self):
        user = koalausers.Users.new(username='test', email_address='foss@lighthouseuk.net', first_name='Test', raw_password='test', last_name='User', language_preference='en')
        self.assertEqual(u'Username', user._properties['username'].title, u'Username Title mismatch')
        self.assertEqual(u'Email', user._properties['email_address'].title, u'Email Title mismatch')
        self.assertEqual(u'First Name', user._properties['first_name'].title, u'First Name Title mismatch')
        self.assertEqual(u'Last Name', user._properties['last_name'].title, u'Last Name Title mismatch')
        self.assertEqual(u'Language Preference', user._properties['language_preference'].title, u'Lang Preference Title mismatch')
        self.assertEqual(u'Password', user._properties['password'].title, u'Password Title mismatch')


class TestUserDatastore(unittest.TestCase):
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

    def tearDown(self):
        self.testbed.deactivate()

    def test_insert_user(self):
        user = koalausers.Users.new(username='test', email_address='foss@lighthouseuk.net', first_name='Test', raw_password='test', last_name='User', language_preference='en')
        user_id = koalausers.Users.insert(resource_object=user)
        self.assertTrue(user_id)

    def test_get_user(self):
        user = koalausers.Users.new(username='test', email_address='foss@lighthouseuk.net', first_name='Test', raw_password='test', last_name='User', language_preference='en')
        user_id = koalausers.Users.insert(resource_object=user)

        retrieved_user = koalausers.Users.get(resource_uid=user_id)
        self.assertTrue(retrieved_user)

    def test_insert_user_stip_filter(self):
        user = koalausers.Users.new(username='test ', email_address='foss@lighthouseuk.net ', first_name='Test ', raw_password='test ', last_name='User ', language_preference='en')
        user_id = koalausers.Users.insert(resource_object=user)

        retrieved_user = koalausers.Users.get(resource_uid=user_id)
        self.assertEqual(retrieved_user.username, 'test', u'Strip whitespace failed')
        self.assertEqual(retrieved_user.email_address, 'foss@lighthouseuk.net', u'Strip whitespace failed')
        self.assertEqual(retrieved_user.first_name, 'Test', u'Strip whitespace failed')
        self.assertEqual(retrieved_user.last_name, 'User', u'Strip whitespace failed')

    def test_insert_user_lowercase_filter(self):
        user = koalausers.Users.new(username='TEST ', email_address='foss@lighthouseuk.net ', first_name='Test ', raw_password='test ', last_name='User ', language_preference='en')
        user_id = koalausers.Users.insert(resource_object=user)

        retrieved_user = koalausers.Users.get(resource_uid=user_id)
        self.assertEqual(retrieved_user.username, 'test', u'String lowercase failed')
        self.assertEqual(retrieved_user.email_address, 'foss@lighthouseuk.net', u'String lowercase failed')

    def test_get_and_verify_username(self):
        user = koalausers.Users.new(username='test', email_address='foss@lighthouseuk.net', first_name='Test', raw_password='test', last_name='User ', language_preference='en')
        user_id = koalausers.Users.insert(resource_object=user)
        retrieved_user = koalausers.Users.get(resource_uid=user_id)

        valid, result = koalausers.Users.get_by_auth_details_and_verify(auth_id='test', password='test')

        self.assertEqual(valid, True, u'Username verification failed')
        self.assertEqual(result.uid, retrieved_user.uid, u'User verification failed')

    def test_get_and_verify_email(self):
        user = koalausers.Users.new(username='test', email_address='foss@lighthouseuk.net', first_name='Test', raw_password='test', last_name='User', language_preference='en')
        user_id = koalausers.Users.insert(resource_object=user)
        retrieved_user = koalausers.Users.get(resource_uid=user_id)

        valid, result = koalausers.Users.get_by_auth_details_and_verify(auth_id='foss@lighthouseuk.net', password='test')

        self.assertEqual(valid, True, u'Email verification failed')
        self.assertEqual(result.uid, retrieved_user.uid, u'User verification failed')

    def test_get_and_verify_invalid_username(self):
        user = koalausers.Users.new(username='test', email_address='foss@lighthouseuk.net', first_name='Test', raw_password='test', last_name='User', language_preference='en')
        koalausers.Users.insert(resource_object=user)

        valid, result = koalausers.Users.get_by_auth_details_and_verify(auth_id='notvalid', password='test')

        self.assertEqual(valid, False, u'User was loaded with invalid details')
        self.assertEqual(result, u'Invalid username or email address', u'User was loaded with invalid details')

    def test_get_and_verify_invalid_email(self):
        user = koalausers.Users.new(username='test', email_address='foss@lighthouseuk.net', first_name='Test', raw_password='test', last_name='User', language_preference='en')
        koalausers.Users.insert(resource_object=user)

        valid, result = koalausers.Users.get_by_auth_details_and_verify(auth_id='notvalid@test.com', password='test')

        self.assertEqual(valid, False, u'User was loaded with invalid details')
        self.assertEqual(result, u'Invalid username or email address', u'User was loaded with invalid details')

    def test_get_and_verify_invalid_password(self):
        user = koalausers.Users.new(username='test', email_address='foss@lighthouseuk.net', first_name='Test', raw_password='test', last_name='User ', language_preference='en')
        koalausers.Users.insert(resource_object=user)

        valid, result = koalausers.Users.get_by_auth_details_and_verify(auth_id='test', password='incorrectpassword')

        self.assertEqual(valid, False, u'User verified with invalid password')
        self.assertEqual(result, u'Password does not match', u'User verified with invalid password')

    def test_update_user(self):
        user = koalausers.Users.new(username='test', email_address='foss@lighthouseuk.net', first_name='Test', raw_password='test', last_name='User', language_preference='en')
        user_uid = koalausers.Users.insert(resource_object=user)
        retrieved_user = koalausers.Users.get(resource_uid=user_uid)
        retrieved_user.first_name = 'Updated'
        koalausers.Users.update(resource_object=retrieved_user)
        updated_user = koalausers.Users.get(resource_uid=user_uid)
        self.assertEqual(updated_user.first_name, 'Updated', u'Update user failed')

    def test_delete_user(self):
        user = koalausers.Users.new(username='test', email_address='foss@lighthouseuk.net', first_name='Test', raw_password='test', last_name='User', language_preference='en')
        user_uid = koalausers.Users.insert(resource_object=user)
        koalausers.Users.delete(resource_uid=user_uid)
        retrieved_user = koalausers.Users.get(resource_uid=user_uid)
        self.assertFalse(retrieved_user)

    def test_insert_search(self):
        user = koalausers.Users.new(username='test', email_address='foss@lighthouseuk.net', first_name='Test', raw_password='test', last_name='User ', language_preference='en')
        koalausers.Users.insert(resource_object=user)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 1, u'Deferred task missing')

        deferred.run(tasks[0].payload)   # Doesn't return anything so nothing to test

        search_result = koalausers.Users.search(query_string='username: test')
        self.assertEqual(search_result.results_count, 1, u'Query returned incorrect count')
        self.assertEqual(len(search_result.results), 1, u'Query returned incorrect number of results')

    def test_update_search(self):
        user = koalausers.Users.new(username='test', email_address='foss@lighthouseuk.net', first_name='Test', raw_password='test', last_name='User ', language_preference='en')
        user_uid = koalausers.Users.insert(resource_object=user)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 1, u'Deferred task missing')

        deferred.run(tasks[0].payload)   # Doesn't return anything so nothing to test

        retrieved_user = koalausers.Users.get(resource_uid=user_uid)
        retrieved_user.first_name = 'Updated'
        koalausers.Users.update(resource_object=retrieved_user)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 2, u'Deferred task missing')

        deferred.run(tasks[1].payload)   # Doesn't return anything so nothing to test

        search_result = koalausers.Users.search(query_string='first_name: Updated')
        self.assertEqual(search_result.results_count, 1, u'Query returned incorrect count')
        self.assertEqual(len(search_result.results), 1, u'Query returned incorrect number of results')

    def test_delete_search(self):
        user = koalausers.Users.new(username='test', email_address='foss@lighthouseuk.net', first_name='Test', raw_password='test', last_name='User ', language_preference='en')
        user_uid = koalausers.Users.insert(resource_object=user)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 1, u'Deferred task missing')

        deferred.run(tasks[0].payload)   # Doesn't return anything so nothing to test

        koalausers.Users.delete(resource_uid=user_uid)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 2, u'Deferred task missing')

        deferred.run(tasks[1].payload)   # Doesn't return anything so nothing to test

        search_result = koalausers.Users.search(query_string='username: test')
        self.assertEqual(search_result.results_count, 0, u'Query returned incorrect count')
        self.assertEqual(len(search_result.results), 0, u'Query returned incorrect number of results')

    def test_unique_user_values(self):
        user = koalausers.Users.new(username='test', email_address='foss@lighthouseuk.net', first_name='Test', raw_password='test', last_name='User', language_preference='en')
        koalausers.Users.insert(resource_object=user)

        with self.assertRaises(koalacore.UniqueValueRequired):
            koalausers.Users.insert(resource_object=user)

    def test_unique_user_value_errors(self):
        user = koalausers.Users.new(username='test', email_address='foss@lighthouseuk.net', first_name='Test', raw_password='test', last_name='User', language_preference='en')
        koalausers.Users.insert(resource_object=user)

        try:
            koalausers.Users.insert(resource_object=user)
        except koalacore.UniqueValueRequired, e:
            self.assertEqual(len(e.errors), 2, u'Incorrect number of unique errors raised')
            self.assertEqual(e.errors[0], 'username', u'Missing unique username error')
            self.assertEqual(e.errors[1], 'email_address', u'Missing unique username error')

    def test_unique_user_update_deletes_old(self):
        user = koalausers.Users.new(username='test', email_address='foss@lighthouseuk.net', first_name='Test', raw_password='test', last_name='User', language_preference='en')
        new_user_uid = koalausers.Users.insert(resource_object=user)

        loaded_user = koalausers.Users.get(resource_uid=new_user_uid)
        loaded_user.email_address = 'test@example.com'
        koalausers.Users.update(resource_object=loaded_user)

        try:
            duplicate_user = koalausers.Users.new(username='test2', email_address='test@example.com', first_name='Test', raw_password='test', last_name='User', language_preference='en')
            koalausers.Users.insert(resource_object=duplicate_user)
        except koalacore.UniqueValueRequired, e:
            self.assertEqual(len(e.errors), 1, u'Incorrect number of unique errors raised')
            self.assertEqual(e.errors[0], 'email_address', u'Missing unique username error')

        old_email_user = koalausers.Users.new(username='test1', email_address='foss@lighthouseuk.net', first_name='Test', raw_password='test', last_name='User', language_preference='en')
        old_email_user_uid = koalausers.Users.insert(resource_object=old_email_user)
        self.assertTrue(old_email_user_uid, u'Old user email failed to create')

    def test_delete_unique_user_values(self):
        # Basically just test that no exception is thrown
        user = koalausers.Users.new(username='test', email_address='foss@lighthouseuk.net', first_name='Test', raw_password='test', last_name='User', language_preference='en')
        user_uid = koalausers.Users.insert(resource_object=user)
        koalausers.Users.delete(resource_uid=user_uid)
        koalausers.Users.insert(resource_object=user)


class TestUserGroup(unittest.TestCase):
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
        group_uid = ndb.Key('Group', 'test_group_uid').urlsafe()

        user = koalausers.Users.new(username='test', email_address='foss@lighthouseuk.net', first_name='Test', raw_password='test', last_name='User ', language_preference='en')
        user_uid = koalausers.Users.insert(resource_object=user)

        self.test_user_group_with_spaces = {
            'group_uid': '  {}  '.format(group_uid),
            'user_uid': '  {}  '.format(user_uid),
            'group_name': '  test_group_name  ',
            'action_set': {'  test_acl_entry  '},
        }
        self.test_user_group = {
            'group_uid': group_uid,
            'user_uid': user_uid,
            'group_name': 'test_group_name',
            'action_set': {'test_acl_entry'},
        }

    def tearDown(self):
        self.testbed.deactivate()

    def test_insert_user_group(self):
        user_group = koalausers.UserGroups.new(**self.test_user_group)
        user_group_uid = koalausers.UserGroups.insert(resource_object=user_group)
        self.assertTrue(user_group_uid)

    def test_get_user_group(self):
        user_group = koalausers.UserGroups.new(**self.test_user_group)
        user_group_uid = koalausers.UserGroups.insert(resource_object=user_group)

        retrieved_user_group = koalausers.UserGroups.get(resource_uid=user_group_uid)
        self.assertTrue(retrieved_user_group, u'Stored value mismatch')
        self.assertTrue(retrieved_user_group.uid, u'Stored value mismatch')
        self.assertTrue(isinstance(retrieved_user_group.created, datetime), u'Stored value mismatch')
        self.assertTrue(isinstance(retrieved_user_group.updated, datetime), u'Stored value mismatch')
        self.assertEqual(retrieved_user_group.group_uid, self.test_user_group['group_uid'], u'Stored group_uid value mismatch')
        self.assertEqual(retrieved_user_group.user_uid, self.test_user_group['user_uid'], u'Stored user_uid value mismatch')
        self.assertEqual(retrieved_user_group.group_name, self.test_user_group['group_name'], u'Stored group_name value mismatch')
        self.assertEqual(retrieved_user_group.action_set, self.test_user_group['action_set'], u'Stored action_set value mismatch')

    def test_get_user_group_by_id(self):
        user_group = koalausers.UserGroups.new(**self.test_user_group)
        user_group_uid = koalausers.UserGroups.insert(resource_object=user_group)

        retrieved_user_group = koalausers.UserGroups.get_by_group_uid(user_uid=self.test_user_group['user_uid'],
                                                                      group_uid=self.test_user_group['group_uid'])

        self.assertTrue(retrieved_user_group, u'Stored value mismatch')
        self.assertTrue(retrieved_user_group.uid, u'Stored value mismatch')
        self.assertTrue(isinstance(retrieved_user_group.created, datetime), u'Stored value mismatch')
        self.assertTrue(isinstance(retrieved_user_group.updated, datetime), u'Stored value mismatch')
        self.assertEqual(retrieved_user_group.group_uid, self.test_user_group['group_uid'], u'Stored group_uid value mismatch')
        self.assertEqual(retrieved_user_group.user_uid, self.test_user_group['user_uid'], u'Stored user_uid value mismatch')
        self.assertEqual(retrieved_user_group.group_name, self.test_user_group['group_name'], u'Stored group_name value mismatch')
        self.assertEqual(retrieved_user_group.action_set, self.test_user_group['action_set'], u'Stored action_set value mismatch')

    def test_insert_user_group_strip_filter(self):
        user_group = koalausers.UserGroups.new(**self.test_user_group_with_spaces)
        user_group_uid = koalausers.UserGroups.insert(resource_object=user_group)

        retrieved_user_group = koalausers.UserGroups.get(resource_uid=user_group_uid)

        self.assertEqual(retrieved_user_group.group_uid, self.test_user_group['group_uid'], u'Stored group_uid value mismatch')
        self.assertEqual(retrieved_user_group.user_uid, self.test_user_group['user_uid'], u'Stored user_uid value mismatch')
        self.assertEqual(retrieved_user_group.group_name, self.test_user_group['group_name'], u'Stored group_name value mismatch')
        self.assertEqual(retrieved_user_group.action_set, self.test_user_group['action_set'], u'Stored action_set value mismatch')

    def test_update_user_group(self):
        user_group = koalausers.UserGroups.new(**self.test_user_group)
        user_group_uid = koalausers.UserGroups.insert(resource_object=user_group)
        retrieved_user_group = koalausers.UserGroups.get(resource_uid=user_group_uid)

        retrieved_user_group.group_name = 'updated_group_name'
        retrieved_user_group.action_set = {'updated_acl_entry'}

        koalausers.UserGroups.update(resource_object=retrieved_user_group)
        updated_user_group = koalausers.UserGroups.get(resource_uid=user_group_uid)

        self.assertEqual(retrieved_user_group.uid, updated_user_group.uid, u'UID mismatch')
        self.assertEqual(retrieved_user_group.created, updated_user_group.created, u'Created date has changed')
        self.assertNotEqual(retrieved_user_group.updated, updated_user_group.updated, u'Updated date not changed')
        self.assertEqual(updated_user_group.group_uid, self.test_user_group['group_uid'], u'Stored group_uid value mismatch')
        self.assertEqual(updated_user_group.user_uid, self.test_user_group['user_uid'], u'Stored user_uid value mismatch')
        self.assertEqual(updated_user_group.group_name, 'updated_group_name', u'Stored group_name value mismatch')
        self.assertEqual(updated_user_group.action_set, {'updated_acl_entry'}, u'Stored action_set value mismatch')

    def test_update_immutable_raises_exception(self):
        user_group = koalausers.UserGroups.new(**self.test_user_group)
        user_group_uid = koalausers.UserGroups.insert(resource_object=user_group)
        retrieved_user_group = koalausers.UserGroups.get(resource_uid=user_group_uid)

        with self.assertRaises(AssertionError) as context:
            retrieved_user_group.group_uid = 'updated_group_uid'

        with self.assertRaises(AssertionError) as context:
            retrieved_user_group.user_uid = 'updated_user_uid'

    def test_delete_user_group(self):
        user_group = koalausers.UserGroups.new(**self.test_user_group)
        user_group_uid = koalausers.UserGroups.insert(resource_object=user_group)
        koalausers.UserGroups.delete(resource_uid=user_group_uid)
        retrieved_user_group = koalausers.UserGroups.get(resource_uid=user_group_uid)
        self.assertFalse(retrieved_user_group)

    def test_delete_user_group_by_uid(self):
        user_group = koalausers.UserGroups.new(**self.test_user_group)
        user_group_uid = koalausers.UserGroups.insert(resource_object=user_group)

        koalausers.UserGroups.delete_by_group_uid(user_uid=self.test_user_group['user_uid'],
                                                  group_uid=self.test_user_group['group_uid'])

        retrieved_user_group = koalausers.UserGroups.get(resource_uid=user_group_uid)
        self.assertFalse(retrieved_user_group)

    def test_insert_search(self):
        user_group = koalausers.UserGroups.new(**self.test_user_group)
        koalausers.UserGroups.insert(resource_object=user_group)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 3, u'Deferred task missing')

        deferred.run(tasks[0].payload)  # Doesn't return anything so nothing to test
        deferred.run(tasks[1].payload)  # Doesn't return anything so nothing to test
        deferred.run(tasks[2].payload)  # Doesn't return anything so nothing to test

        search_result = koalausers.UserGroups.search(
            query_string='group_name: {}'.format(self.test_user_group['group_name']))
        self.assertEqual(search_result.results_count, 1, u'Query returned incorrect count')
        self.assertEqual(len(search_result.results), 1, u'Query returned incorrect number of results')

    def test_update_search(self):
        user_group = koalausers.UserGroups.new(**self.test_user_group)
        user_group_uid = koalausers.UserGroups.insert(resource_object=user_group)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 3, u'Invalid number of Deferred tasks')

        deferred.run(tasks[0].payload)  # Doesn't return anything so nothing to test
        deferred.run(tasks[1].payload)  # Doesn't return anything so nothing to test
        deferred.run(tasks[2].payload)  # Doesn't return anything so nothing to test

        retrieved_user_group = koalausers.UserGroups.get(resource_uid=user_group_uid)
        retrieved_user_group.group_name = 'updated_group_name'
        koalausers.UserGroups.update(resource_object=retrieved_user_group)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 5, u'Invalid number of Deferred tasks')

        deferred.run(tasks[3].payload)  # Doesn't return anything so nothing to test
        deferred.run(tasks[4].payload)  # Doesn't return anything so nothing to test

        search_result = koalausers.UserGroups.search(query_string='group_name: {}'.format('updated_group_name'))
        self.assertEqual(search_result.results_count, 1, u'Query returned incorrect count')
        self.assertEqual(len(search_result.results), 1, u'Query returned incorrect number of results')

    def test_delete_search(self):
        user_group = koalausers.UserGroups.new(**self.test_user_group)
        user_group_uid = koalausers.UserGroups.insert(resource_object=user_group)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 3, u'Invalid number of Deferred tasks')

        deferred.run(tasks[0].payload)  # Doesn't return anything so nothing to test
        deferred.run(tasks[1].payload)  # Doesn't return anything so nothing to test
        deferred.run(tasks[2].payload)  # Doesn't return anything so nothing to test

        self.task_queue.FlushQueue('search-index-update')
        self.task_queue.FlushQueue('deferredwork')

        koalausers.UserGroups.delete(resource_uid=user_group_uid)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 1, u'Invalid number of Deferred tasks')

        deferred.run(tasks[0].payload)  # Doesn't return anything so nothing to test

        search_result = koalausers.UserGroups.search(
            query_string='group_name: {}'.format(self.test_user_group['group_name']))
        self.assertEqual(search_result.results_count, 0, u'Query returned incorrect count')
        self.assertEqual(len(search_result.results), 0, u'Query returned incorrect number of results')

    def test_get_user_groups(self):
        user_group = koalausers.UserGroups.new(**self.test_user_group)
        user_group_uid = koalausers.UserGroups.insert(resource_object=user_group)

        user_groups = koalausers.UserGroups.get_user_groups(user_uid=self.test_user_group['user_uid'])

        self.assertEqual(len(user_groups), 1, u'Incorrect number of user groups returned')
        self.assertEqual(user_groups[0].group_name, self.test_user_group['group_name'], u'Incorrect name returned')

    def test_get_group_users(self):
        user_group = koalausers.UserGroups.new(**self.test_user_group)
        user_group_uid = koalausers.UserGroups.insert(resource_object=user_group)

        group_users = koalausers.UserGroups.get_group_users(group_uid=self.test_user_group['group_uid'])

        self.assertEqual(len(group_users), 1, u'Incorrect number of user groups returned')
        self.assertTrue(isinstance(group_users[0], basestring), u'Incorrect type returned')

    def test_user_groups_property_update(self):
        user_group = koalausers.UserGroups.new(**self.test_user_group)
        user_group_uid = koalausers.UserGroups.insert(resource_object=user_group)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 3, u'Invalid number of Deferred tasks')

        deferred.run(tasks[0].payload)  # Doesn't return anything so nothing to test
        deferred.run(tasks[1].payload)  # Doesn't return anything so nothing to test
        deferred.run(tasks[2].payload)  # Doesn't return anything so nothing to test

        user_groups = koalausers.UserGroups.get_user_groups(user_uid=self.test_user_group['user_uid'])

        self.assertEqual(len(user_groups), 1, u'Incorrect number of user groups returned')
        user = koalausers.Users.get(resource_uid=self.test_user_group['user_uid'])
        self.assertEqual(user.groups, {self.test_user_group['group_uid']: self.test_user_group['group_name']}, u'User groups mismatch')
        self.assertEqual(user.permissions.acl[self.test_user_group['group_uid']], self.test_user_group['action_set'], u'User groups mismatch')

    def test_user_groups_property_delete(self):
        user_group = koalausers.UserGroups.new(**self.test_user_group)
        user_group_uid = koalausers.UserGroups.insert(resource_object=user_group)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 3, u'Invalid number of Deferred tasks')

        deferred.run(tasks[0].payload)  # Doesn't return anything so nothing to test
        deferred.run(tasks[1].payload)  # Doesn't return anything so nothing to test
        deferred.run(tasks[2].payload)  # Doesn't return anything so nothing to test

        self.task_queue.FlushQueue('search-index-update')
        self.task_queue.FlushQueue('deferredwork')

        user_groups = koalausers.UserGroups.get_user_groups(user_uid=self.test_user_group['user_uid'])

        self.assertEqual(len(user_groups), 1, u'Incorrect number of user groups returned')

        koalausers.UserGroups.delete_by_group_uid(user_uid=self.test_user_group['user_uid'], group_uid=self.test_user_group['group_uid'])

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 2, u'Invalid number of Deferred tasks')
        deferred.run(tasks[0].payload)  # Doesn't return anything so nothing to test
        deferred.run(tasks[1].payload)  # Doesn't return anything so nothing to test

        user = koalausers.Users.get(resource_uid=self.test_user_group['user_uid'])
        self.assertEqual(user.groups, {}, u'User groups mismatch')
        self.assertFalse(user_group_uid in user.permissions.acl, u'User groups mismatch')

