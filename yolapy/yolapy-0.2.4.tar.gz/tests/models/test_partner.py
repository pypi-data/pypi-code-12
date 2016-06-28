from unittest import TestCase
from mock import patch

from yolapy.models import Partner


class PartnerTestCase(TestCase):

    def setUp(self):
        self.client_patcher = patch('yolapy.models.partner.Yola')
        self.addCleanup(self.client_patcher.stop)
        self.client = self.client_patcher.start().return_value
        self.client.username = 'WL_DEFAULT'


class TestPartnerMe(PartnerTestCase):

    """Partner.me()."""

    def test_has_available_subscription_types(self):
        Partner.me().available_subscription_types

    @patch.object(Partner, 'fetch_partner_data')
    def test_fetches_data_using_the_client_username(self, fetch):
        Partner.me()
        fetch.assert_called_once_with('WL_DEFAULT')
