from penelope.utils.auth import verify_token


class BearerTokenAuth:

    def __init__(self, token_secret):
        self.token_secret = token_secret

    def process_request(self, req, res):
        try:
            bearer, token = req.auth.split(' ')
        except (ValueError, AttributeError):
            req.context['auth_user'] = None
        else:
            if bearer == 'Bearer':
                req.context['auth_user'] = verify_token(token, secret_key=self.token_secret)
            else:
                req.context['auth_user'] = None
