from flask import request
from raven.contrib.flask import Sentry as BaseSentry
from flask_login import current_user


class Sentry(BaseSentry):

    def before_request(self, *args, **kwargs):
        self.last_event_id = None

    def update_context(self):
        if 'request' not in self.client.context:
            self.client.http_context(self.get_http_info(request))
        if 'user' not in self.client.context:
            self.client.user_context(self.get_user_info(request))

    def get_user_info(self, request):
        user_info = super().get_user_info(request)
        if user_info:
            user_info['username'] = current_user.nickname
        return user_info

    def captureException(self, *args, **kwargs):
        self.update_context()
        super().captureException(*args, **kwargs)

    def captureMessage(self, *args, **kwargs):
        self.update_context()
        super().captureMessage(*args, **kwargs)
