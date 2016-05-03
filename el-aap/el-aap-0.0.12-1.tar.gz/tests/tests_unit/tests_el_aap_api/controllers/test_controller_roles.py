__author__ = 'schlitzer'

from unittest import TestCase
from unittest.mock import Mock, patch

import jsonschema.exceptions

from el_aap_api.controllers import roles
from el_aap_api.errors import InvalidBody


class TestUnitControllerRoles(TestCase):
    def setUp(self):
        request_patcher = patch('el_aap_api.controllers.roles.request', autospec=False)
        self.request = request_patcher.start()

        response_patcher = patch('el_aap_api.controllers.roles.response', autospec=False)
        self.response = response_patcher.start()

    def test_search(self):
        expected = 'blubber'

        def request_query_get(key, default):
            if key == '_id':
                return 'search_ids'
            if key == 'users':
                return 'user1,user2,user3'
            if key == 'fields':
                return None
            return default
        self.request.query.get.side_effect = request_query_get
        m_aa = Mock()
        m_roles = Mock()
        m_roles.search.return_value = expected

        result = roles.search(m_aa, m_roles)

        m_aa.require_admin.assert_called_with()
        m_roles.search.assert_called_with(_ids='search_ids', users='user1,user2,user3', fields=None)
        self.assertEquals(result, expected)

    def test_get(self):
        expected = 'blubber'
        role = 'test::role'

        def request_query_get(key, default):
            if key == 'fields':
                return None
            return default
        self.request.query.get.side_effect = request_query_get

        m_aa = Mock()
        m_roles = Mock()
        m_roles.get.return_value = expected
        result = roles.get(m_aa, m_roles, role)
        m_roles.get.assert_called_with(role, None)
        m_aa.require_admin.assert_called_with()
        self.assertEqual(result, expected)

    def test_create(self):
        request_data = {
            '_id': 'test_role',
            'description': 'some text',
            'users': ['test_user1', 'test_user2']
        }
        self.request.json = request_data
        expected = 'blubber'

        m_aa = Mock()
        m_roles = Mock()
        m_roles.create.return_value = expected
        m_users = Mock()
        m_users.check_ids.return_value = True

        result = roles.create(m_aa, m_roles, m_users)

        m_aa.require_admin.assert_called_with()
        m_roles.create.assert_called_with(request_data)
        m_users.check_ids.assert_called_with(['test_user1', 'test_user2'])
        self.assertEquals(result, expected)

    def test_create_invalid_body(self):
        request_data = {
            '_id': 'test_role',
            'description': 'some text',
            'users': ['test_user1', 'test_user2']
        }
        self.request.json = request_data

        m_aa = Mock()
        m_roles = Mock()
        m_users = Mock()
        m_users.check_ids.return_value = False

        self.assertRaises(InvalidBody, roles.create, m_aa, m_roles, m_users)
        m_aa.require_admin.assert_called_with()
        m_users.check_ids.assert_called_with(['test_user1', 'test_user2'])

    def test_update(self):
        request_data = {
            'description': 'some text',
            'users': ['test_user1', 'test_user2']
        }
        self.request.json = request_data
        expected = 'blubber'

        m_aa = Mock()
        m_roles = Mock()
        m_roles.update.return_value = expected
        m_users = Mock()
        m_users.check_ids.return_value = True

        result = roles.update(m_aa, m_roles, m_users, 'test_role')

        m_aa.require_admin.assert_called_with()
        m_roles.update.assert_called_with('test_role', request_data)
        m_users.check_ids.assert_called_with(['test_user1', 'test_user2'])
        self.assertEquals(result, expected)

    def test_update_invalid_body(self):
        request_data = {
            'description': 'some text',
            'users': ['test_user1', 'test_user2']
        }
        self.request.json = request_data
        expected = 'blubber'

        m_aa = Mock()
        m_roles = Mock()
        m_roles.update.return_value = expected
        m_users = Mock()
        m_users.check_ids.return_value = False

        self.assertRaises(InvalidBody, roles.update, m_aa, m_roles, m_users, 'test_role')

        m_aa.require_admin.assert_called_with()
        m_users.check_ids.assert_called_with(['test_user1', 'test_user2'])

    def test_update_users(self):
        request_data = ['test_user1', 'test_user2']
        self.request.json = request_data
        expected = 'blubber'

        m_aa = Mock()
        m_roles = Mock()
        m_roles.add_users.return_value = expected
        m_users = Mock()
        m_users.check_ids.return_value = True

        result = roles.update_users(m_aa, m_roles, m_users, 'test_role')

        m_aa.require_admin.assert_called_with()
        m_roles.add_users.assert_called_with('test_role', request_data)
        m_users.check_ids.assert_called_with(['test_user1', 'test_user2'])
        self.assertEquals(result, expected)

    def test_update_users_invalid_body_not_list(self):
        request_data = 'test'
        self.request.json = request_data

        m_aa = Mock()
        m_roles = Mock()
        m_users = Mock()
        m_users.check_ids.return_value = True

        self.assertRaises(InvalidBody, roles.update_users, m_aa, m_roles, m_users, 'test_role')

        m_aa.require_admin.assert_called_with()

    def test_update_users_invalid_body_invalid_users(self):
        request_data = ['test_user1', 'test_user2']
        self.request.json = request_data

        m_aa = Mock()
        m_roles = Mock()
        m_users = Mock()
        m_users.check_ids.return_value = False

        self.assertRaises(InvalidBody, roles.update_users, m_aa, m_roles, m_users, 'test_role')

    def test_delete_users(self):
        request_data = ['test_user1', 'test_user2']
        self.request.json = request_data
        expected = 'blubber'

        m_aa = Mock()
        m_roles = Mock()
        m_roles.remove_users.return_value = expected

        result = roles.delete_users(m_aa, m_roles, 'test_role')

        m_aa.require_admin.assert_called_with()
        m_roles.remove_users.assert_called_with('test_role', request_data)
        self.assertEquals(result, expected)

    def test_delete_users_invalid_body_not_list(self):
        request_data = 'test'
        self.request.json = request_data

        m_aa = Mock()
        m_roles = Mock()

        self.assertRaises(InvalidBody, roles.delete_users, m_aa, m_roles,  'test_role')

        m_aa.require_admin.assert_called_with()

    def test_delete(self):
        expected = 'blubber'

        m_aa = Mock()
        m_permissions = Mock()
        m_roles = Mock()
        m_roles.delete.return_value = expected

        result = roles.delete(m_aa, m_roles, m_permissions, 'test_role')

        m_aa.require_admin.assert_called_with()
        m_permissions.remove_role_from_all.assert_called_with('test_role')
        m_roles.delete.assert_called_with('test_role')
        self.assertEquals(result, expected)

