from xdjango.contrib.captcha.recaptcha import ReCaptchaGoogle


def validate_captcha(response, remoteip=None):
    api = ReCaptchaGoogle()

    res = api.verify_captcha(response, remoteip)
    return res and ("success" in res.data) and res.data["success"]