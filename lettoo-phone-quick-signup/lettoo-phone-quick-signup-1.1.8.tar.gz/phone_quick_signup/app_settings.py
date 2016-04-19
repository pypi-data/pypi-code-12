import sys


class AppSettings(object):
    def __init__(self, prefix):
        self.prefix = prefix

    def _setting(self, name, dflt):
        from django.conf import settings
        getter = getattr(settings,
                         'PHONE_QUICK_SIGNUP_SETTING_GETTER',
                         lambda name, dflt: getattr(settings, name, dflt))
        return getter(self.prefix + name, dflt)

    @property
    def PHONE_CONFIRMATION_EXPIRE_MINUTES(self):
        return self._setting("PHONE_CONFIRMATION_EXPIRE_MINUTES", 10)

    @property
    def UNIQUE_PHONE(self):
        """
        Enforce uniqueness of e-mail addresses
        """
        return self._setting("UNIQUE_PHONE", True)

    @property
    def PASSWORD_MIN_LENGTH(self):
        """
        Minimum password Length
        """
        return self._setting("PASSWORD_MIN_LENGTH", 6)

    @property
    def SIGNUP_FORM_CLASS(self):
        """
        Signup form
        """
        return self._setting("SIGNUP_FORM_CLASS", None)

    @property
    def USERNAME_REQUIRED(self):
        """
        The user is required to enter a username when signing up
        """
        return self._setting("USERNAME_REQUIRED", True)

    @property
    def USERNAME_MIN_LENGTH(self):
        """
        Minimum username Length
        """
        return self._setting("USERNAME_MIN_LENGTH", 1)

    @property
    def USERNAME_BLACKLIST(self):
        """
        List of usernames that are not allowed
        """
        return self._setting("USERNAME_BLACKLIST", [])

    @property
    def PASSWORD_INPUT_RENDER_VALUE(self):
        """
        render_value parameter as passed to PasswordInput fields
        """
        return self._setting("PASSWORD_INPUT_RENDER_VALUE", False)

    @property
    def ADAPTER(self):
        return self._setting('ADAPTER', 'phone_quick_signup.adapter.DefaultAccountAdapter')

    @property
    def USER_MODEL_USERNAME_FIELD(self):
        return self._setting('USER_MODEL_USERNAME_FIELD', 'username')

    @property
    def USER_MODEL_PHONE_FIELD(self):
        return self._setting('USER_MODEL_PHONE_FIELD', 'phone')

    @property
    def USER_MODEL_PHONE_VERIFIED_FIELD(self):
        return self._setting('USER_MODEL_PHONE_VERIFIED_FIELD', 'phone_verified')

    @property
    def FORMS(self):
        return self._setting('FORMS', {})

    @property
    def USER_MODEL(self):
        return self._setting('USER_MODEL', 'auth.User')

    @property
    def SENDSMS_BACKEND(self):
        return self._setting('SENDSMS_BACKEND', 'phone_quick_signup.backends.console.SmsBackend')

    @property
    def SENDSMS_DEFAULT_FROM_PHONE(self):
        return self._setting('SENDSMS_DEFAULT_FROM_PHONE', '')

    @property
    def SENDSMS_DEFAULT_BODY(self):
        return self._setting('SENDSMS_DEFAULT_BODY',
                             'Your verification code is: %(key)s, the period of validity is %(expire_minutes)s minutes')

    @property
    def YTX_SERVER_IP(self):
        return self._setting('YTX_SERVER_IP', 'sandboxapp.cloopen.com')

    @property
    def YTX_SERVER_PORT(self):
        return self._setting('YTX_SERVER_PORT', '8883')

    @property
    def YTX_REST_VERSION(self):
        return self._setting('YTX_REST_VERSION', '2013-12-26')

    @property
    def YTX_ACCOUNT_SID(self):
        return self._setting('YTX_ACCOUNT_SID', '')

    @property
    def YTX_ACCOUNT_TOKEN(self):
        return self._setting('YTX_ACCOUNT_TOKEN', '')

    @property
    def YTX_APP_SID(self):
        return self._setting('YTX_APP_SID', '')

    @property
    def RESEND_CONFIRMATION_COOLDOWN_PERIOD_MINUTES(self):
        return self._setting('RESEND_CONFIRMATION_COOLDOWN_PERIOD_MINUTES', 3)

    @property
    def INVALID_AUTO_RESEND_CONFIRMATION(self):
        return self._setting('INVALID_AUTO_RESEND_CONFIRMATION', True)


app_settings = AppSettings('PHONE_QUICK_SIGNUP_')
app_settings.__name__ = __name__
sys.modules[__name__] = app_settings
