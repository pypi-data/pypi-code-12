__author__ = 'schlitzer'

from unittest import TestCase
from unittest.mock import Mock, patch

import jsonschema.exceptions

from el_aap_api.controllers import users


class TestUnitControllerUsers(TestCase):
    def setUp(self):
        request_patcher = patch('el_aap_api.controllers.users.request', autospec=False)
        self.request = request_patcher.start()

        response_patcher = patch('el_aap_api.controllers.users.response', autospec=False)
        self.response = response_patcher.start()

    def test_search(self):
        expected = "blubber"

        def request_query_get(key, default):
            if key == '_id':
                return 'search_ids'
            if key == 'fields':
                return None
            return default
        self.request.query.get.side_effect = request_query_get
        m_aa = Mock()
        m_users = Mock()
        m_users.search.return_value = expected

        result = users.search(m_aa, m_users)

        m_aa.require_admin.assert_called_with()
        m_users.search.assert_called_with(_ids='search_ids', admin=None, fields=None)
        self.assertEquals(result, expected)

    def test_get(self):
        expected = "blubber"
        user = 'test::user'

        def request_query_get(key, default):
            if key == 'fields':
                return None
            return default
        self.request.query.get.side_effect = request_query_get

        m_aa = Mock()
        m_users = Mock()
        m_users.get.return_value = expected
        result = users.get(m_aa, m_users, user)
        m_users.get.assert_called_with(user, None)
        m_aa.require_admin.assert_called_with()
        self.assertEqual(result, expected)

    def test_get_self(self):
        expected = "blubber"
        user = 'testuser'

        def request_query_get(key, default):
            if key == 'fields':
                return None
            return default
        self.request.query.get.side_effect = request_query_get

        m_aa = Mock()
        m_aa.get_user.return_value = 'testuser'
        m_users = Mock()
        m_users.get.return_value = expected

        result = users.get(m_aa, m_users, '_self')

        m_users.get.assert_called_with(user, None)
        m_aa.get_user.assert_called_with()
        self.assertEqual(result, expected)

    def test_create(self):
        request_data = {
            "_id": "test_user",
            "admin": False,
            "email": "testuser@example.com",
            "name": "Test User",
            "password": "password"
        }
        self.request.json = request_data
        expected = "blubber"

        m_aa = Mock()
        m_users = Mock()
        m_users.create.return_value = expected

        result = users.create(m_aa, m_users)

        m_aa.require_admin.assert_called_with()
        m_users.create.assert_called_with(request_data)
        self.assertEquals(result, expected)

    def test_create_invalid_body(self):
        request_data = {
            "email": "testuser@example.com",
            "name": "Test User",
            "password": "password"
        }
        self.request.json = request_data

        m_aa = Mock()
        m_users = Mock()

        self.assertRaises(jsonschema.exceptions.ValidationError, users.create, m_aa, m_users)
        m_aa.require_admin.assert_called_with()

    def test_update(self):
        request_data = {
            "email": "testuser@example.com",
            "name": "Test User",
            "password": "password"
        }
        self.request.json = request_data
        expected = "blubber"

        m_aa = Mock()
        m_users = Mock()
        m_users.update.return_value = expected

        result = users.update(m_aa, m_users, 'test_user')

        m_aa.require_admin.assert_called_with()
        m_users.update.assert_called_with('test_user', request_data)
        self.assertEquals(result, expected)

    def test_update_self(self):
        request_data = {
            "email": "testuser@example.com",
            "admin": True,
            "name": "Test User",
            "password": "password"
        }
        expected_data = {
            "email": "testuser@example.com",
            "name": "Test User",
            "password": "password"
        }
        self.request.json = request_data
        expected = "blubber"

        m_aa = Mock()
        m_aa.get_user.return_value = "testuser"
        m_users = Mock()
        m_users.update.return_value = expected

        result = users.update(m_aa, m_users, '_self')

        m_aa.get_user.assert_called_with()
        m_users.update.assert_called_with('testuser', expected_data)
        self.assertEquals(result, expected)

    def test_update_invalid_body(self):
        request_data = {
            "_id": "test_user",
            "email": "testuser@example.com",
            "name": "Test User",
            "password": "password"
        }
        self.request.json = request_data

        m_aa = Mock()
        m_users = Mock()

        self.assertRaises(jsonschema.exceptions.ValidationError, users.update, m_aa, m_users, 'test_user')
        m_aa.require_admin.assert_called_with()

    def test_delete(self):
        expected = "blubber"

        m_aa = Mock()
        m_users = Mock()
        m_users.delete.return_value = expected
        m_roles = Mock()

        result = users.delete(m_aa, m_users, m_roles, 'test_user')

        m_aa.require_admin.assert_called_with()
        m_users.delete.assert_called_with('test_user')
        m_roles.remove_user_from_all.assert_called_with('test_user')
        self.assertEquals(result, expected)

    def test_delete_self(self):
        expected = "blubber"

        m_aa = Mock()
        m_aa.get_user.return_value = 'self_user'
        m_users = Mock()
        m_users.delete.return_value = expected
        m_roles = Mock()

        result = users.delete(m_aa, m_users, m_roles, '_self')

        m_aa.get_user.assert_called_with()
        m_users.delete.assert_called_with('self_user')
        m_roles.remove_user_from_all.assert_called_with('self_user')
        self.assertEquals(result, expected)

