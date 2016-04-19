import os


class TestConfiguration:
    """
    Class to read user config data
    """
    def __init__(self):
        pass

    @staticmethod
    def get_hub_url():
        return TestConfiguration.get_config_from_env('PSCORE_SELENIUM_HUB_URL', '')

    @staticmethod
    def get_amazon_hub_url():
        return TestConfiguration.get_config_from_env('PSCORE_AMAZON_HUB_URL', '')

    @staticmethod
    def get_sauce_username():
        return TestConfiguration.get_config_from_env('PSCORE_SAUCE_USERNAME', '')

    @staticmethod
    def get_sauce_key():
        return TestConfiguration.get_config_from_env('PSCORE_SAUCE_KEY', '')

    @staticmethod
    def get_sauce_parent_account():
        return TestConfiguration.get_config_from_env('PSCORE_SAUCE_PARENT_ACCOUNT', '')

    @staticmethod
    def get_sauce_tunnel_id():
        return TestConfiguration.get_config_from_env("PSCORE_SAUCE_TUNNEL_ID", None)

    @staticmethod
    def get_execution_environment():
        return TestConfiguration.get_config_from_env('PSCORE_ENVIRONMENT', 'grid')

    @staticmethod
    def get_browser():
        return TestConfiguration.get_config_from_env('PSCORE_BROWSER', 'firefox')

    @staticmethod
    def get_browser_version():
        return TestConfiguration.get_config_from_env('PSCORE_BROWSER_VERSION', '')

    @staticmethod
    def get_browser_resolution():
        return TestConfiguration.get_config_from_env('PSCORE_BROWSER_RESOLUTION', None)

    @staticmethod
    def get_homepage():
        return TestConfiguration.get_config_from_env('PSCORE_HOMEPAGE', '')

    @staticmethod
    def get_screenshot_dir():
        return TestConfiguration.get_config_from_env('PSCORE_SCREENSHOT_DIR', './')

    @staticmethod
    def get_chrome_package_name():
        return TestConfiguration.get_config_from_env('PSCORE_ANDROID_CHROME_PACKAGE_NAME', 'com.android.chrome')

    @staticmethod
    def get_skygrid_enabled():
        str_value = TestConfiguration.get_config_from_env('PSCORE_SKYGRID_ENABLED', False)
        return str_value == 'True'

    @staticmethod
    def get_skygrid_service_url():
        return TestConfiguration.get_config_from_env('PSCORE_SKYGRID_SERVICE_URL', None)

    @staticmethod
    def get_html_dump_on_failure_enabled():
        str_value = TestConfiguration.get_config_from_env('PSCORE_HTML_DUMP_ON_FAILURE', False)
        return str_value == 'True'

    @staticmethod
    def get_user_id():
        import platform
        return TestConfiguration.get_config_from_env('PSCORE_AGENT_ID', platform.node())

    @staticmethod
    def get_sauce_debug_hub_url():
        return TestConfiguration.get_config_from_env('PSCORE_SAUCE_DEBUG_HUB', None)

    @staticmethod
    def get_applitools_lic_key():
        return TestConfiguration.get_config_from_env('PSCORE_APPLITOOLS_LIC_KEY', None)

    @staticmethod
    def get_config_from_env(env_key, default_value):
        env_value = os.getenv(env_key, 'Unspecified')
        if env_value == 'Unspecified':
            return default_value
        return env_value


