from requests.auth import AuthBase

from .HMAC import HMAC


class AmbisafeAuth(AuthBase):
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def __call__(self, request):
        """:param request:
        :type request: requests.PreparedRequest
        :return:
        """
        hmac = HMAC(self.api_secret, request.url, request.method, request.body)
        request.headers['Timestamp'] = hmac.nonce
        request.headers['Signature'] = hmac.signature
        request.headers['API-key'] = self.api_key
        return request
