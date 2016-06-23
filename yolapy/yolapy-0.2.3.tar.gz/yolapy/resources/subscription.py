class SubscriptionResourceMixin(object):
    """Methods for managing Subscription resources."""

    def list_subscriptions(self, **options):
        """Return paginated list of subscriptions.

        >>> yola.list_subscriptions()
        {
            'count': 999,
            'previous': None,
            'next': 'https://wl.qa.yola.net/pr/subscriptions/?page=2',
            'results': [{...}, {...}, ...]
        }

        You can pass ``page_size`` and ``page`` as keyword arguments:

        >>> yola.list_subscriptions(page_size=50, page=2)

        You can also pass filters and odering options as keyword arguments.
        See https://wl.qa.yola.net/subscriptions/ for available options.
        """
        return self.get(self._subscription_path(), params=options).json()

    def get_subscription(self, subscription_id):
        """Return details for a particular subscription.

        >>> subscription = yola.get_subscription('subscription_id')
        >>> subscription['name']
        'My Subscription'
        """
        return self.get(self._subscription_path(subscription_id)).json()

    def change_subscription_type(self, subscription_id, new_type):
        """Change subscription type.

        >>> yola.change_subscription_type('subscription_id', 'new_type')

        See https://wl.qa.yola.net/subscriptions/ for available types.
        """
        return self.post(
            self._subscription_path(subscription_id, 'change_type'),
            data={'new_type': new_type}).json()

    def cancel_subscription(self, subscription_id, reason):
        """Cancel active subscription.

        >>> yola.cancel_subscription('subscription_id', 'some reason')
        """
        return self.post(
            self._subscription_path(subscription_id, 'cancel'),
            data={'reason': reason}).json()

    def reactivate_subscription(self, subscription_id, reason):
        """Re-activate a cancelled subscription.

        >>> yola.reactivate_subscription('subscription_id', 'some reason')
        """
        return self.post(
            self._subscription_path(subscription_id, 'reactivate'),
            data={'reason': reason}).json()

    def activate_trial_subscription(self, subscription_id):
        """Convert trial subscription to active.

        >>> yola.activate_trial_subscription('subscription_id')
        """
        return self.post(
            self._subscription_path(subscription_id, 'remove_trial')).json()

    def create_subscription(self, subscription_type, user_id, properties):
        """Create a new subscription.

        >>> subscription_type = 'wl_basic'
        >>> user_id = 'abcdef0123456789abcdef0123456789'
        >>> properties = {...}
        >>> yola.create_subscription(subscription_type, user_id, properties)

        See https://wl.qa.yola.net/subscriptions/ for available types and
        properties.
        """
        data = {
            'properties': properties,
            'type': subscription_type,
            'user_id': user_id,
        }
        return self.post(self._subscription_path(), data=data).json()

    def _subscription_path(self, *parts):
        path = '/'.join(['subscriptions'] + list(parts))
        return '/%s/' % path
