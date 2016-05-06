from .utils import SettingsBase


class PostNLCheckoutSettings(SettingsBase):
    """ Settings for PostNL checkout. """
    settings_prefix = 'POSTNL_CHECKOUT'

    DEFAULT_TIMEOUT = None
    DEFAULT_ENVIRONMENT = 'sandbox'

    DEFAULT_REDIRECT_URL = 'wishlist'

    DEFAULT_SERVICE_STATUS_CACHE_KEY = 'postnl_checkout_service_status'
    DEFAULT_SERVICE_STATUS_CACHE_TIMEOUT = 60

postnl_checkout_settings = PostNLCheckoutSettings()
