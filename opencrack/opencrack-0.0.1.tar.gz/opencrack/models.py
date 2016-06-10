import logging

from opencrack import utils
from opencrack.exceptions import (KeystoneUnauthorized, KeystoneNotFound,
                                  KeystoneInternalError)


LOG = logging.getLogger(__name__)


class Auth(object):
    """docstring for AuthModel"""
    def __init__(self, method, body, tenant=None, version=3):
        self.method = method
        self.body = body
        self.version = version
        self.tenant = tenant
        self.extra_data = {}

    def as_dict(self):
        if self.version == 2:
            return {
                "auth": {
                    'tenantId': self.tenant,
                    self.method: self.body
                }
            }

        auth_dict = {
            "auth": {
                "identity": {
                    "methods": [self.method],
                    self.method: self.body
                }
            }
        }
        if self.tenant:
            auth_dict['auth']['scope'] = {"project": {
                "id": self.tenant}}
        return auth_dict


class GenericAPIObj(object):
    """ Generic API response wrapper """

    def __init__(self, primary_key=None, headers=None, *args, **kwargs):
        self.primary_key = primary_key
        self.headers = headers

        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    def __len__(self):
        if self.primary_key:
            return len(getattr(self, self.primary_key))

    def __iter__(self):
        if self.primary_key:
            # Create an iterator if we have a primary key defined
            return PrimaryKeyIter(getattr(self, self.primary_key))

    def __repr__(self):
        if self.primary_key:
            return repr(getattr(self, self.primary_key))
        return repr(self)

    def __getitem__(self, key):
        if self.primary_key:
            return getattr(self, self.primary_key)[key]
        return getattr(self, key)


class PrimaryKeyIter(object):
    """ Generic object iterator. Used to allow objects to be iterated. """

    def __init__(self, data):
        self.data = data

    def next(self):
        if not self.data:
            raise StopIteration
        return self.data.pop()

    def __iter__(self):
        return self


class APIDef(object):
    """ API function definition """

    def __init__(self, name, **kwargs):
        self.name = name
        self.defs = kwargs.get('defs')
        self.chained = True if self.defs else False
        self.url = kwargs.get('url')
        self.url_args = kwargs.get('url_args')
        self.method = kwargs.get('method', 'POST')
        self.content_type = kwargs.get('content_type', 'application/json')
        self.primary_key = kwargs.get('primary_key')

    def get_url(self, url_vars=None):
        """
        Renders a URL for the API request.
        """
        if not self.url_args:
            return self.url

        rendered_url = self.url

        if isinstance(url_vars, basestring):
            # vargs is a single arg passed (probably a PK/id, before a dataset
            rendered_url = rendered_url.replace(
                '$' + self.url_args[0],
                url_vars)
        else:
            # url is more complex, and has multiple variables that need filling
            # and are passed in as keyword args.
            for arg in self.url_args:
                rendered_url = rendered_url.replace(
                    '$' + arg,
                    url_vars.get(arg))

        assert '$' not in rendered_url, (
            'URL missing args, requires %s, provided %s' % (
                self.url_args, url_vars))

        return rendered_url

    def _wrap_call(self, token):
        """
        Generates an API caller function and returns it on demand, the
        caller is curried with the client's own data.

        :arg token:
            API Request token that the API call will use, as the client can
            be defined once, most API calls will need to be authenticated
            and the token passed here will be passed into the generated
            function
        :returns: callable
        """
        def make_call(*args, **kwargs):
            """
            Generic make_call method which executes API requests for client
            def objects.

            We accept multiple method signatures to conform with existing
            openstack library methods.

            make_call()
                makes a simple call to the APIDef url.

            make_call('xx-yy-zz')
                builds a dynamic url with no body, usually for deletes & gets.

            make_call({ .. })
                passes the provided data structure to the static url.

            make_call('xx-yy-zz', { .. })
                passes the provided data structure to a dynamic url, with
                the first argument being the first, and only, url_args arg

            make_call(arg_1=x, arg_2=y)
                renders a complex dynamic url with multiple parts where the
                keys align with the APIDef provided url_args.

            """
            data = None

            if len(args) == 1:
                if isinstance(args[0], basestring):
                    kwargs = args[0]
                else:
                    data = args[0]
            elif len(args) == 2:
                data = args[1]
                kwargs = args[0]

            rendered_url = self.get_url(kwargs)

            res = utils.api_request(
                rendered_url,
                token,
                data,
                self.method,
                self.content_type)

            headers = res.headers
            resp_code = res.status_code

            if resp_code == 401:
                raise KeystoneUnauthorized()
            elif resp_code == 404:
                raise KeystoneNotFound()
            elif resp_code >= 500:
                raise KeystoneInternalError()
            elif resp_code == 204:
                return None

            body = res.json()

            return GenericAPIObj(
                primary_key=self.primary_key, headers=headers, **body)

        return make_call


class KeystoneClient(object):
    """ Simulated Keystone Client """

    def __init__(self, *args, **kwargs):
        self.username = kwargs.get('username')
        self.user_id = kwargs.get('user_id')
        self.password = kwargs.get('password')
        self.token = None
        self.token_id = kwargs.get('token', kwargs.get('token_id'))
        self.catalog = None
        self.user_roles = None
        self.auth_url = kwargs.get('auth_url')
        self.tenant = kwargs.get('tenant',
                                 kwargs.get('tenant_id',
                                            kwargs.get('tenant_name')))
        self.config = kwargs.get('config')
        self.raw_token = None

        if not self.token_id and self.username and self.password:
            self._password_auth()

    def __getattr__(self, name):
        if self.__dict__.get(name):
            return self.__dict__[name]

        apidef = self._lookup(name)
        if apidef.chained:
            client = KeystoneClient(token=self.token_id,
                                    auth_url=self.auth_url, config=apidef.defs)
            return client
        return apidef._wrap_call(self.token_id)

    def _lookup(self, name):
        for apidef in self.config:
            if apidef.name == name:
                return apidef
        raise AttributeError

    def _password_auth(self):
        """ Override """
        raise NotImplementedError


class KeystoneV2Client(KeystoneClient):
    def __init__(self, *args, **kwargs):
        super(KeystoneV2Client, self).__init__(*args, **kwargs)
        self.config = kwargs.get('config', [APIDef(
            'tenants',
            defs=[
                APIDef('list', url='%s/tenants' % self.auth_url,
                       method='GET', primary_key='tenants')
            ]),
            APIDef('tokens',
                   defs=[
                       APIDef('authenticate', url='%s/tokens' % self.auth_url,
                              method='POST', primary_key='access')
                   ])
        ])

    def _password_auth(self):
        if self.username and self.password:
            pw_auth = Auth(
                'passwordCredentials',
                {
                    'username': self.username,
                    'password': self.password
                }, tenant=self.tenant)
            pw_auth.version = 2
            token_ref = utils.api_request(
                "%s/tokens" % self.auth_url, None, pw_auth.as_dict())

            if token_ref.status_code >= 400:
                raise Exception
            self.raw_token = token_ref.json()['access']
            self.token = token_ref.json()['access']['token']
            self.token_id = self.token['id']
            self.catalog = token_ref.json()['access']['serviceCatalog']
            self.user_roles = token_ref.json()['access']['user']['roles']

        if not self.token_id:
            raise Exception


class KeystoneV3Client(KeystoneClient):
    def __init__(self, *args, **kwargs):
        super(KeystoneV3Client, self).__init__(*args, **kwargs)
        self.config = kwargs.get('config', [
            APIDef('tenants',
                   defs=[
                       APIDef('list',
                              url='%s/users/%s/projects' % (
                                  self.auth_url, self.user_id),
                              method='GET',
                              primary_key='projects')
                   ]),
            APIDef('users',
                   defs=[
                       APIDef('update_password',
                              url='%s/users/%s' % (
                                  self.auth_url, self.user_id),
                              method='PATCH',
                              primary_key='user')
                   ]),
            APIDef('otp_seeds',
                   defs=[
                       APIDef('list',
                              url='%s/users/%s/OS-OTP/seeds' % (
                                  self.auth_url, self.user_id),
                              method='GET',
                              primary_key='seeds'),
                       APIDef('create',
                              url='%s/users/%s/OS-OTP/seeds' % (
                                  self.auth_url, self.user_id),
                              method='POST',
                              primary_key='seed'),
                       APIDef('test',
                              url='%s/users/%s/OS-OTP/seeds/$seed_id/test' % (
                                  self.auth_url, self.user_id),
                              url_args=['seed_id'],
                              method='POST'),
                       APIDef('delete',
                              url='%s/users/%s/OS-OTP/seeds/$seed_id' % (
                                  self.auth_url, self.user_id),
                              url_args=['seed_id'],
                              method='DELETE'),
                       APIDef('qr_code',
                              url='%s/users/%s/OS-OTP/seeds/$seed_id/qr' % (
                                  self.auth_url, self.user_id),
                              url_args=['seed_id'],
                              method='GET'),
                   ]),
            APIDef('tokens',
                   defs=[
                       APIDef('authenticate',
                              url='%s/auth/tokens' % (self.auth_url),
                              method='POST',
                              primary_key='token'),
                   ]),
        ])

    def _password_auth(self):
        if self.username and self.password:
            pw_auth = Auth(
                'password',
                {
                    "user": {
                        "domain": {"id": "default"},
                        "name": self.username,
                        "password": self.password
                    }
                })
            token_ref = utils.api_request(
                '%s/auth/tokens' % self.auth_url, None, pw_auth.as_dict())
            self.token_id = token_ref.headers['X-Subject-Token']
            self.raw_token = token_ref.json()
            self.token = self.raw_token['token']

        if not self.token_id:
            raise Exception('no token')
