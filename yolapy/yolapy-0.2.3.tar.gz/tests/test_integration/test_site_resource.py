from tests.test_integration.helpers import (
    create_site, create_user_with_subscription)
from tests.test_integration.test_case import YolaServiceTestCase
from yolapy.models import Site


class TestYolaSite(YolaServiceTestCase):
    """Yola: Site resource"""

    @classmethod
    def setUpClass(cls):
        super(TestYolaSite, cls).setUpClass()
        cls.site = create_site(cls.service)

    def test_list_sites(self):
        sites = self.service.list_sites(page_size=999)['results']
        site_ids = [s['id'] for s in sites]
        self.assertIn(self.site['id'], site_ids)

    def test_get_site(self):
        exptected_site_id = self.site['id']
        site = self.service.get_site(exptected_site_id)
        self.assertEqual(site['id'], exptected_site_id)

    def test_disable_and_enable_site(self):
        self.service.disable_site(self.site['id'])
        self.service.enable_site(self.site['id'])
        # no way to verify? just checking it doesn't raise for now...

    def test_change_site_owner(self):
        new_user = create_user_with_subscription(self.service)
        self.service.change_site_owner(self.site['id'], new_user['id'])

        site = self.service.get_site(self.site['id'])
        self.assertEqual(site['user_id'], new_user['id'])

    def test_delete_and_undelete_site(self):
        self.service.delete_site(self.site['id'])
        site = self.service.get_site(self.site['id'])
        self.assertTrue(site['deleted_at'])

        self.service.undelete_site(self.site['id'])
        site = self.service.get_site(self.site['id'])
        self.assertFalse(site['deleted_at'])

    def test_list_sites_using_model(self):
        sites = Site.list()
        site_ids = [s.id for s in sites]
        self.assertIn(self.site['id'], site_ids)
