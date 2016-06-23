from demands import JSONServiceClient
from yolapy.configuration import config as defaults
from yolapy.resources import campaign, partner, site, subscription, user


class Yola(
        JSONServiceClient, campaign.CampaignResourceMixin,
        partner.PartnerResourceMixin, site.SiteResourceMixin,
        subscription.SubscriptionResourceMixin, user.UserResourceMixin):
    """Client for Yola's API.

    If using yolapy.configuration::

        configure(
            url='https://wl.yola.net/',
            auth=('username', 'password'))
        yola = Yola()
        yola.get_user('user_id')

    Or configured manually::

        yola = Yola(
            url='https://wl.yola.net/',
            auth=('username', 'password'))
        yola.get_user('user_id')

    When appropriate, successful responses will return parsed json objects.

    Failures will raise instances of ``demands.HTTPServiceError``.
    """

    def __init__(self, **kwargs):
        """Initialize with optional headers.

        Auth and url defaults are pulled from yolapy.configuration.

        Passed arguments will override configuration::

            Yola(headers={'Header-Name': 'value'})
        """
        config = {}
        config.update(defaults)
        config.update(kwargs)
        assert(config['url'])
        assert(config['auth'])
        self.username = config['auth'][0]
        super(Yola, self).__init__(**config)
