__author__ = 'schlitzer'

from unittest import TestCase
from unittest.mock import Mock, patch

import jsonschema.exceptions

from el_aap_api.controllers import permissions
from el_aap_api.errors import InvalidBody


class TestUnitControllerPermissions(TestCase):
    def setUp(self):
        request_patcher = patch('el_aap_api.controllers.permissions.request', autospec=False)
        self.request = request_patcher.start()

        response_patcher = patch('el_aap_api.controllers.permissions.response', autospec=False)
        self.response = response_patcher.start()

    def test_search(self):
        expected = 'blubber'

        def request_query_get(key, default):
            if key == '_id':
                return 'search_ids'
            if key == 'roles':
                return 'test_role1,test_role2'
            if key == 'scope':
                return "test_scope"
            if key == 'permissions':
                return ":perm"
            if key == 'fields':
                return None
            return default
        self.request.query.get.side_effect = request_query_get
        m_aa = Mock()
        m_permission = Mock()
        m_permission.search.return_value = expected

        result = permissions.search(m_aa, m_permission)

        m_aa.require_admin.assert_called_with()
        m_permission.search.assert_called_with(
            scope='test_scope',
            permissions=':perm',
            roles='test_role1,test_role2',
            fields=None,
            _ids='search_ids'
        )
        self.assertEquals(result, expected)

    def test_get(self):
        expected = 'blubber'
        permission = 'test::permission'

        def request_query_get(key, default):
            if key == 'fields':
                return None
            return default
        self.request.query.get.side_effect = request_query_get

        m_aa = Mock()
        m_permissions = Mock()
        m_permissions.get.return_value = expected
        result = permissions.get(m_aa, m_permissions, permission)
        m_permissions.get.assert_called_with(permission, None)
        m_aa.require_admin.assert_called_with()
        self.assertEqual(result, expected)

    def test_create(self):
        request_data = {
            '_id': 'test_permission',
            'description': 'some text',
            'permissions': [':cluster:monitor', ':index:crud:'],
            'roles': ['test_role1', 'test_role2'],
            'scope': 'testindex-*'
        }
        self.request.json = request_data
        expected = 'blubber'

        m_aa = Mock()
        m_permissions = Mock()
        m_permissions.create.return_value = expected
        m_roles = Mock()
        m_roles.check_ids.return_value = True

        result = permissions.create(m_aa, m_permissions, m_roles)

        m_aa.require_admin.assert_called_with()
        m_permissions.create.assert_called_with(request_data)
        m_roles.check_ids.assert_called_with(['test_role1', 'test_role2'])
        self.assertEquals(result, expected)

    def test_create_invalid_body(self):
        request_data = {
            '_id': 'test_permission',
            'description': 'some text',
            'permissions': [':cluster:monitor', ':index:crud:'],
            'roles': ['test_role1', 'test_role2'],
            'scope': 'testindex-*'
        }
        self.request.json = request_data
        expected = 'blubber'

        m_aa = Mock()
        m_permissions = Mock()
        m_permissions.create.return_value = expected
        m_roles = Mock()
        m_roles.check_ids.return_value = False

        self.assertRaises(InvalidBody, permissions.create, m_aa, m_permissions, m_roles)

        m_aa.require_admin.assert_called_with()
        m_roles.check_ids.assert_called_with(['test_role1', 'test_role2'])

    def test_update(self):
        request_data = {
            'description': 'some text',
            'permissions': [':cluster:monitor', ':index:crud:'],
            'roles': ['test_role1', 'test_role2'],
            'scope': 'testindex-*'
        }
        self.request.json = request_data
        expected = 'blubber'

        m_aa = Mock()
        m_permissions = Mock()
        m_permissions.update.return_value = expected
        m_roles = Mock()
        m_roles.check_ids.return_value = True

        result = permissions.update(m_aa, m_permissions, m_roles, 'test_permission')

        m_aa.require_admin.assert_called_with()
        m_permissions.update.assert_called_with('test_permission', request_data)
        m_roles.check_ids.assert_called_with(['test_role1', 'test_role2'])
        self.assertEquals(result, expected)

    def test_update_invalid_body(self):
        request_data = {
            'description': 'some text',
            'permissions': [':cluster:monitor', ':index:crud:'],
            'roles': ['test_role1', 'test_role2'],
            'scope': 'testindex-*'
        }
        self.request.json = request_data
        expected = 'blubber'

        m_aa = Mock()
        m_permissions = Mock()
        m_permissions.update.return_value = expected
        m_roles = Mock()
        m_roles.check_ids.return_value = False

        self.assertRaises(InvalidBody, permissions.update, m_aa, m_permissions, m_roles, 'test_permission')

        m_aa.require_admin.assert_called_with()
        m_roles.check_ids.assert_called_with(['test_role1', 'test_role2'])

    def test_update_permissions(self):
        request_data = [':cluster:', ':index:crud:read']
        self.request.json = request_data
        expected = 'blubber'

        m_aa = Mock()
        m_permissions = Mock()
        m_permissions.add_permissions.return_value = expected

        result = permissions.update_permissions(m_aa, m_permissions, 'test_permission')

        m_aa.require_admin.assert_called_with()
        m_permissions.add_permissions.assert_called_with('test_permission', request_data)
        self.assertEquals(result, expected)

    def test_update_permissions_invalid(self):
        request_data = [':cluster:', ':index:crud:readdddd']
        self.request.json = request_data
        expected = 'blubber'

        m_aa = Mock()
        m_permissions = Mock()
        m_permissions.add_permissions.return_value = expected

        self.assertRaises(jsonschema.exceptions.ValidationError, permissions.update_permissions, m_aa, m_permissions, 'test_permission')

        m_aa.require_admin.assert_called_with()

    def test_update_roles(self):
        request_data = ['test_role1', 'test_role2']
        self.request.json = request_data
        expected = 'blubber'

        m_aa = Mock()
        m_permissions = Mock()
        m_permissions.add_roles.return_value = expected
        m_roles = Mock()
        m_roles.check_ids.return_value = True

        result = permissions.update_roles(m_aa, m_permissions, m_roles, 'test_permission')

        m_aa.require_admin.assert_called_with()
        m_permissions.add_roles.assert_called_with('test_permission', request_data)
        m_roles.check_ids.assert_called_with(['test_role1', 'test_role2'])
        self.assertEquals(result, expected)

    def test_update_roles_invalid_body_not_list(self):
        request_data = 'test'
        self.request.json = request_data

        m_aa = Mock()
        m_permissions = Mock()
        m_roles = Mock()
        m_roles.check_ids.return_value = True

        self.assertRaises(InvalidBody, permissions.update_roles, m_aa, m_permissions, m_roles, 'test_role')

        m_aa.require_admin.assert_called_with()

    def test_update_roles_invalid_body_invalid_users(self):
        request_data = ['test_user1', 'test_user2']
        self.request.json = request_data

        m_aa = Mock()
        m_permissions = Mock()
        m_roles = Mock()
        m_roles.check_ids.return_value = False

        self.assertRaises(InvalidBody, permissions.update_roles, m_aa, m_permissions, m_roles, 'test_role')

    def test_delete_permissions(self):
        request_data = [':cluster:', ':index:crud:read']
        self.request.json = request_data
        expected = 'blubber'

        m_aa = Mock()
        m_permissions = Mock()
        m_permissions.remove_permissions.return_value = expected

        result = permissions.delete_permissions(m_aa, m_permissions, 'test_permission')

        m_aa.require_admin.assert_called_with()
        m_permissions.remove_permissions.assert_called_with('test_permission', request_data)
        self.assertEquals(result, expected)

    def test_delete_permissions_invalid_body_not_list(self):
        request_data = 'test'
        self.request.json = request_data

        m_aa = Mock()
        m_permissions = Mock()

        self.assertRaises(InvalidBody, permissions.delete_permissions, m_aa, m_permissions, 'test_permission')

        m_aa.require_admin.assert_called_with()

    def test_delete_roles(self):
        request_data = ['test_role1', 'test_role2']
        self.request.json = request_data
        expected = 'blubber'

        m_aa = Mock()
        m_permissions = Mock()
        m_permissions.remove_roles.return_value = expected

        result = permissions.delete_roles(m_aa, m_permissions, 'test_permission')

        m_aa.require_admin.assert_called_with()
        m_permissions.remove_roles.assert_called_with('test_permission', request_data)
        self.assertEquals(result, expected)

    def test_delete_roles_invalid_body_not_list(self):
        request_data = 'test'
        self.request.json = request_data

        m_aa = Mock()
        m_permissions = Mock()

        self.assertRaises(InvalidBody, permissions.delete_roles, m_aa, m_permissions, 'test_permission')

        m_aa.require_admin.assert_called_with()

    def test_delete(self):
        expected = 'blubber'

        m_aa = Mock()
        m_permissions = Mock()
        m_permissions.delete.return_value = expected

        result = permissions.delete(m_aa, m_permissions, 'test_permission')

        m_aa.require_admin.assert_called_with()
        m_permissions.delete.assert_called_with('test_permission')
        self.assertEquals(result, expected)

