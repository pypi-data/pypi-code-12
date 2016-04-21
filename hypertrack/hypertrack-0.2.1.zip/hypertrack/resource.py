import sys
import json

try:
    # Python 3
    from urllib.parse import urljoin
except ImportError:
    # Python 2
    from urlparse import urljoin

import requests

import hypertrack
from hypertrack import exceptions, version


class HyperTrackObject(dict):
    '''
    Base HyperTrack object
    '''
    def __init__(self, *args, **kwargs):
        self._unsaved_keys = set()
        super(HyperTrackObject, self).__init__(*args, **kwargs)

    def __setattr__(self, k, v):
        if k[0] == '_' or k in self.__dict__:
            return super(HyperTrackObject, self).__setattr__(k, v)
        else:
            self[k] = v

    def __getattr__(self, k):
        if k[0] == '_':
            raise AttributeError(k)

        try:
            return self[k]
        except KeyError as err:
            raise AttributeError(*err.args)

    def __delattr__(self, k):
        del self[k]

    def __setitem__(self, k, v):
        super(HyperTrackObject, self).__setitem__(k, v)
        self._unsaved_keys.add(k)

    def __delitem__(self, k):
        super(HyperTrackObject, self).__delitem__(k)
        self._unsaved_keys.remove(k)

    @property
    def hypertrack_id(self):
        return self.id

    def __repr__(self):
        ident_parts = [type(self).__name__]

        if isinstance(self.get('object'), basestring):
            ident_parts.append(self.get('object'))

        if isinstance(self.get('id'), basestring):
            ident_parts.append('id=%s' % (self.get('id'),))

        unicode_repr = '<%s at %s> JSON: %s' % (
            ' '.join(ident_parts), hex(id(self)), str(self))

        if sys.version_info[0] < 3:
            return unicode_repr.encode('utf-8')
        else:
            return unicode_repr

    def __str__(self):
        return json.dumps(self, sort_keys=True, indent=2)


class ListObject(HyperTrackObject):
    '''
    '''
    def __init__(self, object_class, **kwargs):
        '''
        '''
        super(ListObject, self).__init__(**kwargs)
        self.results = [object_class(**obj) for obj in self.results]

    def __iter__(self):
        '''
        '''
        return getattr(self, 'results', []).__iter__()


class APIResource(HyperTrackObject):
    '''
    Defines the base HyperTrack API resource
    '''
    resource_url = None

    @classmethod
    def _get_secret_key(cls):
        return hypertrack.secret_key

    @classmethod
    def _get_base_url(cls):
        return hypertrack.base_url

    @classmethod
    def _get_user_agent(cls):
        '''
        '''
        user_agent = 'HyperTrack/v1 PythonBindings/{version}'.format(
            version=version.VERSION)
        return user_agent

    @classmethod
    def _get_headers(cls, has_files=False):
        '''
        '''
        headers = {
            'Authorization': 'token %s' % cls._get_secret_key(),
            'User-Agent': cls._get_user_agent(),
        }

        if not has_files:
            headers['Content-Type'] = 'application/json'

        return headers

    @classmethod
    def _make_request(cls, method, url, data=None, params=None, files=None):
        '''
        '''
        #TODO: Handle file uploads cleanly
        if data and not files:
            data = json.dumps(data)

        if files:
            headers = cls._get_headers(has_files=True)
        else:
            headers = cls._get_headers(has_files=False)

        try:
            resp = requests.request(method, url, headers=headers, data=data,
                                    params=params, files=files, timeout=20)
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as excp:
            msg = ('Unexpected error communicating with HyperTrack.  '
                   'If this problem persists, let us know at '
                   'contact@hypertrack.io. %s')
            err = '%s: %s' % (type(excp).__name__, str(excp))
            raise exceptions.APIConnectionException(msg % err)

        if not 200 <= resp.status_code < 300:
            cls._handle_api_error(resp)

        return resp

    @classmethod
    def _handle_api_error(cls, response):
        '''
        '''
        if response.status_code in [401, 403]:
            raise exceptions.AuthenticationException(response.content,
                                                     response.content,
                                                     response.status_code)
        elif response.status_code == 429:
            raise exceptions.RateLimitException(response.content,
                                                response.content,
                                                response.status_code)
        elif response.status_code in [400, 404]:
            raise exceptions.InvalidRequestException(response.content,
                                                     response.content,
                                                     response.status_code)
        else:
            raise exceptions.APIException(response.content,
                                          response.content,
                                          response.status_code)

    @classmethod
    def get_class_url(cls):
        '''
        '''
        url = urljoin(cls._get_base_url(), cls.resource_url)
        return url

    def get_instance_url(self):
        '''
        '''
        url = urljoin(self._get_base_url(),
                      '{resource_url}{resource_id}/'.format(
                          resource_url=self.resource_url, resource_id=self.id))
        return url


class CreateMixin(object):
    '''
    '''
    @classmethod
    def create(cls, files=None, **data):
        url = cls.get_class_url()
        resp = cls._make_request('post', url, data=data, files=files)
        return cls(**resp.json())


class RetrieveMixin(object):
    '''
    '''
    @classmethod
    def retrieve(cls, hypertrack_id):
        url = urljoin(cls._get_base_url(),
                      '{resource_url}{resource_id}/'.format(
                          resource_url=cls.resource_url,
                          resource_id=hypertrack_id))
        resp = cls._make_request('get', url)
        return cls(**resp.json())


class ListMixin(object):
    '''
    '''
    @classmethod
    def list(cls, **params):
        url = urljoin(cls._get_base_url(), cls.resource_url)
        resp = cls._make_request('get', url, params=params)
        return ListObject(cls, **resp.json())


class UpdateMixin(object):
    '''
    '''
    def save(self, files=None):
        url = self.get_instance_url()
        data = {k: getattr(self, k) for k in self._unsaved_keys}
        resp = self._make_request('patch', url, data=data, files=files)
        self._unsaved_keys = set()
        return self.__class__(**resp.json())


class DeleteMixin(object):
    '''
    '''
    def delete(self):
        pass


class Customer(APIResource, CreateMixin, RetrieveMixin, UpdateMixin, ListMixin):
    '''
    '''
    resource_url = 'customers/'


class Destination(APIResource, CreateMixin, RetrieveMixin, UpdateMixin,
                  ListMixin):
    '''
    '''
    resource_url = 'destinations/'


class Fleet(APIResource, CreateMixin, RetrieveMixin, UpdateMixin, ListMixin):
    '''
    '''
    resource_url = 'fleets/'


class Driver(APIResource, CreateMixin, RetrieveMixin, UpdateMixin, ListMixin):
    '''
    '''
    resource_url = 'drivers/'

    @classmethod
    def create(cls, **data):
        '''
        '''
        if 'photo' in data:
            files = {'photo': data.pop('photo')}
        else:
            files = None

        super(Driver, cls).create(files=files, **data)

    def save(self):
        '''
        '''
        if 'photo' in self._unsaved_keys:
            files = {'photo': self.photo}
            self._unsaved_keys.remove('photo')
        else:
            files = None

        super(Driver, self).save(files=files)


class Hub(APIResource, CreateMixin, RetrieveMixin, UpdateMixin, ListMixin):
    '''
    '''
    resource_url = 'hubs/'


class Task(APIResource, CreateMixin, RetrieveMixin, UpdateMixin, ListMixin):
    '''
    '''
    resource_url = 'tasks/'


class Trip(APIResource, CreateMixin, RetrieveMixin, UpdateMixin, ListMixin):
    '''
    '''
    resource_url = 'trips/'


class GPSLog(APIResource, CreateMixin, RetrieveMixin, ListMixin):
    '''
    '''
    resource_url = 'gps/'


class Event(APIResource, RetrieveMixin, ListMixin):
    '''
    '''
    resource_url = 'events/'
