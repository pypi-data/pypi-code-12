from django.test import TestCase, override_settings


class SettingsTest(TestCase):

    def test_defaults(self):
        """
        Verifies that settings are initialized with defaults
        """
        from newrelic_plugin_agent.conf import settings, DEFAULTS
        self.assertEqual(settings.TIMESLICE_LOCK_RETRY_DELAY_MS, DEFAULTS['TIMESLICE_LOCK_RETRY_DELAY_MS'])
        self.assertEqual(settings.NEWRELIC_BASE_URL, DEFAULTS['NEWRELIC_BASE_URL'])
        self.assertEqual(settings.NEWRELIC_LICENSE_KEY, DEFAULTS['NEWRELIC_LICENSE_KEY'])
        with self.assertRaises(AttributeError):
            assert(settings.FOO)

    @override_settings(
        NEWRELIC_PLUGIN_AGENT={'TIMESLICE_LOCK_RETRY_DELAY_MS': 500})
    def test_user_settings(self):
        """
        Verifies that user settings are applied correctly
        """
        from newrelic_plugin_agent.conf import settings, DEFAULTS
        self.assertEqual(settings.TIMESLICE_LOCK_RETRY_DELAY_MS, 500)
        self.assertEqual(settings.NEWRELIC_BASE_URL, DEFAULTS['NEWRELIC_BASE_URL'])
        self.assertEqual(settings.NEWRELIC_LICENSE_KEY, DEFAULTS['NEWRELIC_LICENSE_KEY'])

    def test_reload(self):
        from newrelic_plugin_agent.conf import settings, DEFAULTS, reload_api_settings
        self.assertEqual(settings.TIMESLICE_LOCK_RETRY_DELAY_MS, DEFAULTS['TIMESLICE_LOCK_RETRY_DELAY_MS'])
        reload_api_settings(setting='NEWRELIC_PLUGIN_AGENT', value={'TIMESLICE_LOCK_RETRY_DELAY_MS': 500})
        from newrelic_plugin_agent.conf import settings
        self.assertEqual(settings.TIMESLICE_LOCK_RETRY_DELAY_MS, 500)
