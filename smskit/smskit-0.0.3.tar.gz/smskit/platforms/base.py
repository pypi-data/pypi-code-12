"""smskit platforms base."""


class BaseHandler(object):
    """BaseHandler."""

    def send(self, phone, content):
        """Send sms."""
        raise NotImplementedError()

    def query_balance(self, **kwargs):
        """Query balance."""
        raise NotImplementedError()
