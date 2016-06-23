from unittest import TestCase

from mock import patch

from yolapy.models import Subscription


class SubscriptionTestCase(TestCase):
    fake_subscription_data = {
        'id': 'fake-sub-id-abcdef1234567890abcd',
        'auto_renew': False,
        'billing_date': '2000-01-01',
        'deprovision_date': '2000-01-01',
        'expiry_date': '2000-01-01',
        'start_date': '2000-01-01',
        'status': 'active',
        'sku': 123,
        'type': 'wl_basic',
        'user_id': 'fake-user-id-abcdef1234567890abc',
        'term': 'P1M',
    }

    def setUp(self):
        self._mock_client()
        self._stub_list_subscriptions()

    def _mock_client(self):
        self.client_patcher = patch('yolapy.models.subscription.Yola')
        self.addCleanup(self.client_patcher.stop)
        self.client = self.client_patcher.start().return_value

    def _stub_list_subscriptions(self):
        self.client.list_subscriptions.return_value = {
            'results': [self.fake_subscription_data],
        }


class TestSubscription(SubscriptionTestCase):
    def test_has_expected_attributes(self):
        sub = Subscription(**self.fake_subscription_data)
        for key, value in self.fake_subscription_data.items():
            self.assertEqual(getattr(sub, key), value)


class SubscriptionList(SubscriptionTestCase):

    """Subscription.list()."""

    def test_fetches_subs_by_passing_arguments_to_client(self):
        Subscription.list(foo='bar', user_id='user-id')
        self.client.list_subscriptions.assert_called_with(
            foo='bar', user_id='user-id')

    def test_creates_subs_using_response(self):
        subs = Subscription.list()
        self.assertEqual(len(subs), 1)
        subscription = subs[0]
        self.assertEqual(subscription.id, 'fake-sub-id-abcdef1234567890abcd')


class SubscriptionProperties(SubscriptionTestCase):

    """Subscription.properties['partner_id']."""

    def test_uses_the_client_config_as_a_default(self):
        self.client.username = 'partner-id-foo123'
        sub = Subscription()
        self.assertEqual(sub.properties['partner_id'], 'partner-id-foo123')
