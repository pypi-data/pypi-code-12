from tests.test_integration.helpers import create_partner
from tests.test_integration.test_case import YolaServiceTestCase


class TestYolaPartners(YolaServiceTestCase):
    """Yola: Partner resource"""

    @classmethod
    def setUpClass(cls):
        super(TestYolaPartners, cls).setUpClass()
        cls.partner = create_partner(cls.service)
        cls.partner_id = cls.partner['id']
        # There's no way to really delete the test partners we're creating :(

    def test_create_partner(self):
        self.assertEqual(self.partner['properties']['website'], 'example.com')

    def test_get_partner(self):
        partner = self.service.get_partner(self.partner_id)
        self.assertEqual(partner['name'], 'TEST')

    def test_delete_partner(self):
        partner = create_partner(self.service)
        self.service.delete_partner(partner['id'])
        partner = self.service.get_partner(partner['id'])
        self.assertFalse(partner['is_active'])

    def test_update_partner(self):
        partner = create_partner(self.service, name='Original Name')
        partner = self.service.update_partner(partner['id'], name='New Name')
        self.assertEqual(partner['name'], 'New Name')

    def test_list_partners(self):
        response = self.service.list_partners(page_size=1)
        self.assertEqual(len(response['results']), 1)
