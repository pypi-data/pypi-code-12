"""smskit factory."""


class SMSFactory(object):
    """SMS factory."""

    def __init__(self, implcls, config):
        self.implcls = implcls
        self.config = config

    def get_class(self):
        """Get class."""
        return self.implcls

    def get_instance(self):
        """Get instance."""
        return self.implcls(config=self.config)
