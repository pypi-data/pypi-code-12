from tests.test_integration.test_case import YolaServiceTestCase

from tests.test_integration.helpers import create_partner, create_user


class TestYolaSubscription(YolaServiceTestCase):
    """Yola: Subscription resource"""

    @classmethod
    def setUpClass(cls):
        super(TestYolaSubscription, cls).setUpClass()
        cls.partner = create_partner(cls.service, properties={
            'website': 'example.com',
            'available_subscription_types': ['wl_basic', 'wl_lite']
        })

        user = create_user(cls.service, partner_id=cls.partner['id'])
        cls.subscription = cls.service.create_subscription(
            'wl_basic', user['id'], {'foo': 'bar'})

    def test_create_subscriptions(self):
        self.assertEqual(self.subscription['status'], 'active')

    def test_list_subscriptions(self):
        subs = self.service.list_subscriptions()['results']
        self.assertTrue(len(subs) > 0)

    def test_get_subscription(self):
        sub = self.service.get_subscription(self.subscription['id'])
        self.assertEqual(sub['id'], self.subscription['id'])

    def test_cancel_and_reactivate_subscription(self):
        self.assertEqual(self.subscription['status'], 'active')

        self.service.cancel_subscription(self.subscription['id'], 'testing')
        cancelled_sub = self.service.get_subscription(self.subscription['id'])
        self.assertEqual(cancelled_sub['status'], 'canceled')

        self.service.reactivate_subscription(cancelled_sub['id'], 'testing')
        reactivated_sub = self.service.get_subscription(cancelled_sub['id'])
        self.assertEqual(reactivated_sub['status'], 'active')

    def test_can_activate_a_trial_subscription(self):
        user = create_user(self.service, partner_id=self.partner['id'])
        sub = self.service.create_subscription(
            'wl_basic', user['id'], {'trial': True})
        self.assertTrue(sub['properties']['trial'])

        activated_sub = self.service.activate_trial_subscription(sub['id'])
        self.assertFalse(activated_sub['properties'].get('trial'))

    def test_can_change_subscription_type(self):
        user = create_user(self.service, partner_id=self.partner['id'])
        sub = self.service.create_subscription(
            'wl_basic', user['id'], {'trial': True})
        self.assertEqual(sub['type'], 'wl_basic')

        modified_sub = self.service.change_subscription_type(
            sub['id'], 'wl_lite')
        self.assertEqual(modified_sub['type'], 'wl_lite')
