from django.conf import settings

from sdklib.http import HttpSdk


class ReCaptchaGoogle(HttpSdk):

    DEFAULT_HOST = "https://www.google.com"

    API_SITE_VERIFY_URL = "/recaptcha/api/siteverify"

    def __init__(self, api_key=None, secret_key=None):
        super(ReCaptchaGoogle, self).__init__()
        self.apiKey = api_key or settings.RECAPTCHA_API_KEY if hasattr(settings, 'RECAPTCHA_API_KEY') else None
        self.secretKey = secret_key or settings.RECAPTCHA_SECRET_KEY if hasattr(settings, 'RECAPTCHA_SECRET_KEY') else None
        if not self.apiKey or not self.secretKey:
            raise ValueError(
                "RECAPTCHA_API_KEY and RECAPTCHA_SECRET_KEY are required."
            )

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
        return self._http_request("POST", self.API_SITE_VERIFY_URL, body_params=params)