import datetime
import time
import ordereddict
import hmac
import hashlib
from query_encoder import QueryEncoder

__author__ = 'erickponce'


class AuthenticationError(Exception):
    pass


class ArgumentError(Exception):
    pass


class SignatureException(Exception):
    pass


class Token(object):

    key = None
    secret = None

    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    def sign(self, request):
        request.sign(self)


class Request(object):

    path = None
    query_dict = None
    auth_dict = None
    method = None
    signed = False

    ISO8601 = datetime.datetime.today().strftime("%Y-%m-%dT%H:%M:%SZ")

    AUTH_VERSION = '1.0'

    def __init__(self, method, path, query):
        if not isinstance(path, str):
            raise ArgumentError('Expected string')
        if not isinstance(query, dict):
            raise ArgumentError('Expected dict')

        query_dict = {}
        auth_dict = {}

        for key, value in query.iteritems():
            key = key.lower()
            if 'auth_' in key:
                auth_dict[key] = value
            else:
                query_dict[key] = value

        self.method = method.upper()
        self.path = path
        self.query_dict = query_dict
        self.auth_dict = auth_dict
        self.signed = False

    def get_auth_field(self, field):
        field = 'auth_' + field
        if field not in self.auth_dict:
            raise AuthenticationError('Missing parameter: {field}'.format(field=field))
        return self.auth_dict.get(field, None)

    # Sign the request with the given token, and return the computed
    # authentication parameters
    def sign(self, token):
        self.auth_dict = dict(
            auth_version='1.0',
            auth_key=token.key,
            auth_timestamp=int(time.time())
        )
        self.auth_dict['auth_signature'] = self.signature(token)
        self.signed = True
        return self.auth_dict

    def authenticate(self, token, raise_exception=True, timestamp_grace=600):
        # Validate that your code has provided a valid token. This does not
        # raise an AuthenticationError since passing tokens with empty secret is
        # a code error which should be fixed, not reported to the API's consumer
        if token.secret is None or token.secret is '':
            raise SignatureException('Provided token is missing secret')

        try:
            self.validate_version()
            self.validate_timestamp(timestamp_grace)
            self.validate_signature(token)
        except AuthenticationError as e:
            # Raise exception again if raise param is True
            # else simply return False
            if raise_exception:
                raise e
            else:
                return False
        return True

    # Expose the authentication parameters for a signed request
    @property
    def _auth_dict(self):
        if not self.signed:
            raise SignatureException('Request not signed')
        return self.auth_dict

    # Query parameters merged with the computed authentication parameters
    @property
    def signed_params(self):
        return dict(self.query_dict.items() + self.auth_dict.items())

    def parameter_string(self):
        param_hash = dict(self.query_dict.items() + (self.auth_dict.items() or {}))
        # Convert keys to lowercase strings
        params_dict = {}
        for key, value in param_hash.iteritems():
            params_dict[key.lower()] = value

        # Exclude signature from signature generation!
        if 'auth_signature' in params_dict:
            del params_dict['auth_signature']

        params_dict = ordereddict.OrderedDict(sorted(params_dict.items()))
        params_list = []
        for key, value in params_dict.iteritems():
            params_list.append(QueryEncoder.encode_param_without_escaping(key, value))
        return '&'.join(params_list)

    def string_to_sign(self):
        return "\n".join([self.method, self.path, self.parameter_string()])

    def signature(self, token):
        return hmac.new(str(token.secret), self.string_to_sign(), hashlib.sha256).hexdigest()

    def validate_version(self):
        if 'auth_version' not in self.auth_dict:
            raise AuthenticationError('Version required')
        if self.auth_dict.get('auth_version') != self.AUTH_VERSION:
            raise AuthenticationError('Version not supported')
        return True

    def validate_timestamp(self, timestamp_grace):
        if not timestamp_grace:
            return True
        timestamp = self.get_auth_field('timestamp')
        error = (time.time() - int(timestamp))

        if error >= timestamp_grace:
            error_message = '''
                Timestamp expired: Given timestamp
                ({timestamp}) not within {timestamp_grace} of server time ({now})
            '''.format(timestamp=timestamp, timestamp_grace=timestamp_grace, now=int(time.time()))
            raise AuthenticationError(error_message)
        return True

    def validate_signature(self, token):
        auth_signature = self.get_auth_field('signature')

        if not auth_signature == self.signature(token):
            error_message = '''
                Invalid signature: you should have
                sent HmacSHA256Hex({string_to_sign}, your_secret_key)
                , but you sent {auth_signature}
            '''.format(string_to_sign=self.string_to_sign(), auth_signature=auth_signature)
            raise AuthenticationError(error_message)
        return True
