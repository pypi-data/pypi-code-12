from yolapy.services import Yola


class Partner(object):

    """Yola Partner service model.

    Example use:
    ```
    > from yolapy.models import Partner
    > Partner.me().available_subscription_types
    ["wl_lite", "wl_premium", "wl_basic", "wl_ecommerce_basic"]
    ```
    """

    def __init__(self):
        self.client = Yola()
        self._partner = None

    def fetch_partner_data(self, partner_id):
        self._partner = self.client.get_partner(partner_id)

    @property
    def available_subscription_types(self):
        properties = self._partner['properties']
        return properties['available_subscription_types']

    @classmethod
    def me(cls):
        partner = cls()
        partner_id = partner.client.username
        partner.fetch_partner_data(partner_id)
        return partner
