class CallerSettings(object):
    def __init__(self):
        self.RF_HOST = '0.0.0.0'
        self.RF_PORT = 8100
        self.SIP_HOST = '0.0.0.0'
        self.SIP_PORT = 5060

    def configure(self, custom_settings):
        for setting in dir(custom_settings):
            setattr(self, setting, getattr(custom_settings, setting))


settings = CallerSettings()

try:
    import settings as proj_settings
except ImportError:
    proj_settings = None

if proj_settings:
    settings.configure(proj_settings)
