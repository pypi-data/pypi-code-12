import json

from django.conf import settings

from sdklib import SdkBase


class Response():
    def __init__(self, content):
        self.data = json.loads(content)


class ReCaptchaGoogle(SdkBase):

    API_HOST = "www.google.com"
    API_PORT = 443
    API_SCHEME = "https"

    API_SITE_VERIFY_URL = "/recaptcha/api/siteverify"

    def __init__(self, api_key=None, secret_key=None):
        self.apiKey = api_key or settings.RECAPTCHA_API_KEY if hasattr(settings, 'RECAPTCHA_API_KEY') else None
        self.secretKey = secret_key or settings.RECAPTCHA_SECRET_KEY if hasattr(settings, 'RECAPTCHA_SECRET_KEY') else None
        if not self.apiKey or not self.secretKey:
            raise ValueError(
                "RECAPTCHA_API_KEY and RECAPTCHA_SECRET_KEY are required."
            )

    def _http(self, method, url, headers=None, params=None, url_params=None):
        _, data, _ = super(ReCaptchaGoogle, self)._http(method, url, headers, params, url_params)
        encoded_data = data.decode('utf8')
        return Response(encoded_data)

    def verify_captcha(self, captcha_response, remoteip=None):
        """

        :param captcha_response: Required. The user response token provided by the reCAPTCHA to the user and provided to
        your site on.
        :param remoteip: Optional. The user's IP address.
        :return: The response is a JSON object:
                {
                  "success": true|false,
                  "error-codes": [...]   // optional
                }
        """
        params = {"secret": self.secretKey, "response": captcha_response}
        return self._http("POST", self.API_SITE_VERIFY_URL, None, params)