from yolapy.services import Yola


class Subscription(object):

    """Construct a Subscription.

    The data in a Subscription instance does not persist until it has
    been saved.

    :param auto_renew: Bool
    :param billing_date: Datetime
    :param deprovision_date: Datetime
    :param expiry_date: Datetime
    :param start_date: Datetime
    :param status: Str, subscription status
    :param term: Str, subscription billing term
    :param id: Str, subscription's 32 char ID
    :param properties: Dict, subscription properties. If unset will be
        defaulted to the client's configured username:
        ``{"partner_id": "<CLIENT_USERNAME>"}``.
    :param sku: Int
    :param type: Str, subscription type
    :param user_id: Str, 32 character ID of the sub's user

    :return: Subscription
    :rtype: yolapy.models.Subscription

    """

    def __init__(
            self, auto_renew=False, billing_date=None, deprovision_date=None,
            expiry_date=None, id=None, properties=None, sku=None,
            start_date=None, status=None, term=None, type=None, user_id=None):
        self.client = Yola()

        self.auto_renew = auto_renew
        self.billing_date = billing_date
        self.deprovision_date = deprovision_date
        self.id = id
        self.properties = properties or {}
        self.properties.setdefault('partner_id', self.client.username)
        self.sku = sku
        self.type = type
        self.user_id = user_id
        self.expiry_date = expiry_date
        self.start_date = start_date
        self.status = status
        self.term = term

    @classmethod
    def list(cls, **kwargs):
        """Return a filtered list of Subscriptions.

        Useage::

           >>> from yolapy.models import Subscription
           >>> user_id = 'abcdef1234567890abcdef1234567890'
           >>> user_subs = Subscription.list(user_id=user_id)
           >>> print user_subs[0]
           <yolapy.models.subscription.Subscription object>
           >>> print user_subs[0].user_id
           u'abcdef1234567890abcdef1234567890'
        """
        response = Yola().list_subscriptions(**kwargs)
        return [cls(**sub) for sub in response['results']]
