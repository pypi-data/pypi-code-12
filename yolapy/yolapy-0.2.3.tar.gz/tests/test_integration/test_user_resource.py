import demands

from tests.test_integration.helpers import (
    create_site, create_user_with_subscription)
from tests.test_integration.test_case import YolaServiceTestCase


class TestYolaUser(YolaServiceTestCase):
    """Yola: User resource"""

    @classmethod
    def setUpClass(cls):
        super(TestYolaUser, cls).setUpClass()
        cls.user = cls._create_user()
        cls.user_id = cls.user['id']

    @classmethod
    def _create_user(cls, **custom_attrs):
        custom_attrs.setdefault('name', 'John')
        return create_user_with_subscription(cls.service, **custom_attrs)

    def test_create_user(self):
        self.assertEqual(self.user['name'], 'John')

    def test_update_user(self):
        user = self._create_user(name='Original Name')
        user = self.service.update_user(user['id'], name='New Name')
        self.assertEqual(user['name'], 'New Name')

    def test_get_user(self):
        user = self.service.get_user(self.user_id)
        self.assertEqual(user['name'], 'John')

    def test_list_users(self):
        response = self.service.list_users(page_size=1)
        self.assertEqual(len(response['results']), 1)

    def test_request_filtered_user_list(self):
        response = self.service.list_users(id=self.user_id)
        self.assertEqual(len(response['results']), 1)
        self.assertEqual(response['results'][0]['id'], self.user_id)

    def test_delete_user(self):
        user = self._create_user()
        self.service.delete_user(user['id'])
        with self.assertRaises(demands.HTTPServiceError):
            self.service.get_user(user['id'])

    def test_get_sso_create_site_url(self):
        url = self.service.get_sso_create_site_url(self.user_id, 'example.com')
        self.assertTrue(url.startswith('http'))

    def test_get_sso_open_site_url(self):
        create_site(self.service, self.user_id)
        url = self.service.get_sso_open_site_url(self.user_id)
        self.assertTrue(url.startswith('http'))
