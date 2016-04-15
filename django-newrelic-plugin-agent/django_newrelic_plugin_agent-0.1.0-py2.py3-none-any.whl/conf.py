from django.conf import settings as django_settings
from django.test.signals import setting_changed


DEFAULTS = {
    # wait one second between retries to obtain lock on metric timeslice
    'TIMESLICE_LOCK_RETRY_DELAY_MS': 1000,
    # base url for newrelic plugin api
    'NEWRELIC_BASE_URL': 'https://platform-api.newrelic.com',
    # license key for newrelic account
    'NEWRELIC_LICENSE_KEY': 'keyboardcat',
}


class Settings(object):

    def __init__(self, user_settings=None):
        if user_settings:
            self._user_settings = user_settings
        self.defaults = DEFAULTS

    @property
    def user_settings(self):
        # cache settings
        if not hasattr(self, '_user_settings'):
            self._user_settings = getattr(django_settings, 'NEWRELIC_PLUGIN_AGENT', {})
        return self._user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults.keys():
            raise AttributeError("Invalid newrelic agent setting: '%s'" % attr)
        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]
        # Cache the result
        setattr(self, attr, val)
        return val

settings = Settings()


def reload_api_settings(*args, **kwargs):
    global settings
    setting, value = kwargs['setting'], kwargs['value']
    if setting == 'NEWRELIC_PLUGIN_AGENT':
        settings = Settings(value)


setting_changed.connect(reload_api_settings)
