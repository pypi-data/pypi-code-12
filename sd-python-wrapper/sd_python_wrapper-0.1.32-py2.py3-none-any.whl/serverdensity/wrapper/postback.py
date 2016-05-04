from hashlib import md5
import json

from serverdensity.wrapper.jsonobject import JsonObject
from serverdensity import Response


class Postback(JsonObject):

    PATHS = {
        'create': '/alerts/postbacks',
    }

    def _validation(self, data):
        """Not Needed"""
        pass

    def create(self, payload, account_name, **kwargs):
        kwargs.setdefault('headers', {})['X-Forwarded-Host'] = account_name + '.serverdensity.io'
        payload = json.dumps(payload)
        kwargs.setdefault('data', {})['payload'] = payload
        kwargs['data']['hash'] = md5(payload.encode('utf-8')).hexdigest()
        return Response(self.api.post(url=self.PATHS['create'], **kwargs))
