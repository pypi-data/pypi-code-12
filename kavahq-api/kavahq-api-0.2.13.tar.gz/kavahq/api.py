# -*- coding: utf-8 -*-
import os
import urlparse
import logging

# thirdparty:
import requests

# internals:
from .exceptions import UnauthorizedError, ApiError

logger = logging.getLogger(__name__)


def enable_debug():
    logger.setLevel(logging.DEBUG)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - '
                                  '%(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)
    logger.addHandler(ch)


class ApiChildren(object):
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.__children_list_data = []

    @property
    def children_list_data(self):
        if not self.__children_list_data:
            self.__children_list_data = self.parent.response
            for key in self.config['keys_path_to_list']:
                self.__children_list_data = self.__children_list_data[key]
        return self.__children_list_data

    def __getitem__(self, index):
        return self.parent.get(self.children_list_data[index][
            self.config['subpath_key']])


class ApiObject(object):
    def __init__(self, path, api, data=None):
        self.internaluse_path = path
        self.internaluse_api = api
        self.internaluse_data = data or {}
        self._response = None

        children_config = api.ALLOWED_PATHS.get(path, {}
                                                ).get('children_config')
        if children_config:
            self.children = ApiChildren(self, children_config)
        else:
            self.children = []

        self.__chained_apis = {}
        return

    def __getattr__(self, name):
        if not name.endswith('/'):
            name = name + '/'
        is_project_details = (
            self.internaluse_path not in self.internaluse_api.ALLOWED_PATHS and
            self.internaluse_path.startswith('project/')
        )
        if is_project_details:
            subpath = os.path.join('project/', name)
        else:
            subpath = os.path.join(self.internaluse_path, name)
        if subpath not in self.__chained_apis:
            self.__chained_apis[subpath] = ApiObject(subpath,
                                                     self.internaluse_api,
                                                     self.internaluse_data)

        return self.__chained_apis[subpath]
    
    def __call__(self, **kwargs):
        self.internaluse_data = kwargs
        return self

    def __getitem__(self, key):
        # special case for /kavauser/username/
        split = self.internaluse_path.split('/')
        if split[0] == 'kavauser' and (len(split) == 1 or not split[1]):
            self.internaluse_path = "kavauser/%s/" % key
            return self.response

        if isinstance(key, (int, long)) and self.children:
            raise TypeError("Please use api_object.children[i] instead. "
                            "ApiObject should be used as dict")
        return self.response[key]

    def __unicode__(self):
        return u"<ApiObject '{self.internaluse_path}'"\
            "?{self.internaluse_data} >".format(self=self)

    def __repr__(self):
        return str(self.__unicode__())

    def __eq__(self, other):
        return (
            self.internaluse_path == other.internaluse_path and
            self.internaluse_data == other.internaluse_data
        )

    def __iter__(self):
        # allows to run dict(api_object_instance)
        return self.response.iterkeys()

    def keys(self):
        return self.response.keys()

    def __hash__(self):
        # this will allow to use ApiObject instances as dict keys
        return (self.internaluse_path, self._method,
                self.internaluse_data_hash).__hash__()

    def get(self, subpath=None, **kwargs):
        new_data = dict(self.internaluse_data)
        new_data.update(kwargs)

        # special handling for projects
        if subpath and self.internaluse_path == 'project/':
            new_data['project_slug'] = subpath
            new_data['project'] = subpath

        path = self.internaluse_path
        if subpath:
            if not subpath.endswith('/'):
                subpath = subpath + '/'
            path = os.path.join(path, subpath)

        return ApiObject(path, self.internaluse_api, new_data)

    @property
    def response(self):
        entry = self.internaluse_api.ALLOWED_PATHS.get(self.internaluse_path,
                                                       {})
        nocache = entry.get('nocache', False)
        # special handling for projects/xxx/plan
        if self.internaluse_path == 'project/plan/':
            self.internaluse_path = 'project/%s/plan/' % (
                self.internaluse_data['project'])
        # special handling for projects/xxx/insurnace
        if self.internaluse_path == 'project/insurance/':
            self.internaluse_path = 'project/%s/insurance/' % (
                self.internaluse_data['project'])
        # special handling for project/xxx/time_spent_gen
        if self.internaluse_path == 'project/time_spent_gen/':
            self.internaluse_path = 'project/%s/time_spent_gen/' % (
                self.internaluse_data['project'])

        if nocache or self._response is None:
            self._response = self.internaluse_api._make_request(
                self.internaluse_path, self.internaluse_data)
        return self._response

    def _data_hash(self):
        keys = tuple(sorted(self.internaluse_data.keys()))
        values = tuple([self.internaluse_data[key] for key in keys])
        return tuple(keys, values).__hash__()


class KavaApi(object):
    ALLOWED_PATHS = {
        'arbitrary_data/': {
            'method': 'post',
            'auth': 'api_key',
            'nocache': True,
            },
        'project/add/': {
            'method': 'post',
            'accepts_company': True,
            'auth': 'basic',
            },
        'project/edit/': {
            'method': 'post',
            'accepts_company': True,
            'auth': 'basic',
            },
        'project/tickets/': {
            'method': 'post',  # orly? maybe should change api to GET?
            'accepts_company': True,
            'auth': 'basic',
            },
        'project/tickets/count/': {
            'method': 'get',
            'accepts_company': True,
            'auth': 'api_key',
            },
        'project/estimate/': {
            'method': 'get',
            'accepts_company': True,
            'auth': 'api_key',
            },
        'project/properties/': {
            'method': 'post',  # orly? maybe should change api to GET?
            'accepts_company': True,
            'auth': 'basic',
            },
        'project/plan/': {
            'method': 'get',
            'accepts_company': False,
            'auth': 'api_key',
        },
        'project/insurance/': {
            'method': 'get',
            'accepts_company': False,
            'auth': 'api_key',
        },
        'project/time_spent_gen/': {
            'method': 'post',
            'accepts_company': True,
            'auth': 'basic',
        },

        'kavauser/by_score/': {
            'method': 'post',
            'accepts_company': True,
            'auth': 'basic',
            },
        'ticket/estimate/': {
            'method': 'get',
            'accepts_company': True,
            'auth': 'api_key',
            'nocache': True,
            },
        'ticket/add/': {
            'method': 'post',
            'accepts_company': True,
            'auth': 'basic',
            },
        'ticket/comment/': {
            'method': 'post',
            'accepts_company': True,
            'auth': 'basic',
            },

        'project/': {
            'children_config': {
                'keys_path_to_list': ('projects',),
                'subpath_key': 'slug',
                },
            },
    }

    def __init__(
            self,
            username,
            password,
            api_key=None,
            base_url='https://kavahq.com/api/',
            company_name=None):
        self.username = username
        self.password = password
        self.base_url = base_url
        self.api_key = api_key
        self.company_name = company_name
        self.__root_api = ApiObject('', self)

    def __getattr__(self, name):
        if name == 'projects':  # just to be more meaningful
            name = 'project'
        return getattr(self.__root_api, name)

    def get_api_key(self):
        self.api_key = self._make_request('apikey/login/')['key']

    def _make_request(self, resource_uri, data=None):
        url = urlparse.urljoin(self.base_url, resource_uri)
        data = data or {}
        data = dict(data)
        method = self.ALLOWED_PATHS.get(resource_uri, {}).get('method', 'get')
        # for project/xxx/time_spent_gen
        if 'time_spent_gen' in resource_uri:
            method = 'post'

        if method == 'get':
            data_key = 'params'
        elif method == 'post':
            data_key = 'data'
        requests_method = getattr(requests, method)

        accepts_company = self.ALLOWED_PATHS.get(resource_uri, {}
                                                 ).get('accepts_company')

        if accepts_company and not 'company' in data:
            data['company'] = self.company_name

        requires_api_key = self.ALLOWED_PATHS.get(resource_uri, {}
                                                  ).get('auth') == 'api_key'
        # special case for /kavauser/username/
        split = resource_uri.split('/')
        if split[0] == 'kavauser':
            if split[1] != 'by_score':
                requires_api_key = True
        # case for /project/xxx/plan/ and /project/xxx/insurance/
        if split[0] == 'project':
            if len(split) > 2 and split[2] in ('plan', 'insurance'):
                requires_api_key = True

        requests_method_kwargs = {data_key: data}

        if requires_api_key:
            self.get_api_key()
            requests_method_kwargs['headers'] = {
                'Authorization': 'ApiKey %s:%s' % (self.username,
                                                   self.api_key)}
        else:
            requests_method_kwargs['auth'] = (self.username, self.password)

        if resource_uri == 'arbitrary_data/':  # EVIL HACK!!!
            import json
            requests_method_kwargs[data_key] = json.dumps(data)
        response = requests_method(url, **requests_method_kwargs)
        logger.debug(unicode(response))

        if response.status_code == 401:
            raise UnauthorizedError(response.text)
        elif response.status_code >= 400:
            error_msg = response.text
            try:
                error_msg = response.json()['errors']
                error_msg = response.json()['message']['errors']
            except Exception:
                pass
            raise ApiError(error_msg)

        try:
            return response.json()['message']
        except KeyError:
            return response.json()
