from unittest import TestCase

from mock import patch

from yolapy.constants import SiteStates
from yolapy.models import Site


class SiteTestCase(TestCase):
    def setUp(self):
        yola_patcher = patch('yolapy.models.site.Yola')
        self.yola = yola_patcher.start().return_value
        self.addCleanup(yola_patcher.stop)


class TestSite(SiteTestCase):
    def test_sets_init_kwargs_as_attributes(self):
        site = Site(name='my site', id='123')
        self.assertEqual(site.name, 'my site')
        self.assertEqual(site.id, '123')


class TestSiteGet(SiteTestCase):
    """Site.get"""

    def test_instantiates_site_with_attrs_from_service(self):
        self.yola.get_site.return_value = {'name': 'site name', 'id': '456'}

        site = Site.get('456')

        self.yola.get_site.assert_called_once_with('456')
        self.assertEqual(site.name, 'site name')
        self.assertEqual(site.id, '456')


class TestSiteList(SiteTestCase):
    """Site.list"""

    def setUp(self):
        super(TestSiteList, self).setUp()

        self.yola.list_sites.return_value = {'results': [
            {'id': '1'}, {'id': '2'},
        ]}

        self.sites = Site.list(user_id='user123')
        _, self.service_kwargs = self.yola.list_sites.call_args

    def test_instantiates_list_of_sites_with_attrs_from_service(self):
        self.assertEqual(len(self.sites), 2)
        self.assertIn(Site(id='1'), self.sites)
        self.assertIn(Site(id='2'), self.sites)

    def test_filters_sites_by_passed_fields(self):
        self.assertEqual(self.service_kwargs['user_id'], 'user123')

    def test_handles_pagination_automatically(self):
        self.assertIn('page', self.service_kwargs)


class TestSiteIsPublished(SiteTestCase):
    """Site.is_published"""

    def test_false_if_no_publishing_data(self):
        site = Site()
        self.assertFalse(site.is_published)

    def test_false_if_publishing_state_is_not_published(self):
        site = Site(publishing_data={'state': 999})
        self.assertFalse(site.is_published)

    def test_true_if_publishing_state_is_published(self):
        site = Site(publishing_data={'state': SiteStates.PUBLISHED})
        self.assertTrue(site.is_published)
