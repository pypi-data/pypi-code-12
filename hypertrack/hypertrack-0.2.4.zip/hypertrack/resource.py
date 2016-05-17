import sys
import json

try:
    # Python 3
    from urllib import parse as urlparse
except ImportError:
    # Python 2
    import urlparse

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

        # Python 3 compatibility for string types
        try:
            basestring
        except NameError:
            basestring = str

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


class APIResource(HyperTrackObject):
    '''
    Defines the base HyperTrack API resource
    '''
    resource_url = None

    @classmethod
    def _get_secret_key(cls):
        '''
        Returns the secret key to be used for the API request
        '''
        return hypertrack.secret_key

    @classmethod
    def _get_base_url(cls):
        '''
        Returns the base URL to be used for the API request
        '''
        return hypertrack.base_url

    @classmethod
    def _get_user_agent(cls):
        '''
        Returns user agent for the API request
        '''
        user_agent = 'HyperTrack/v1 PythonBindings/{version}'.format(
            version=version.VERSION)
        return user_agent

    @classmethod
    def _get_headers(cls, has_files=False):
        '''
        Returns headers for the API request
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
        Makes the network call to the API
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
        Raises appropriate exceptions for API errors
        '''
        if response.status_code in [401, 403]:
            raise exceptions.AuthenticationException(response.content,
                                                     response.content,
                                                     response.status_code,
                                                     response.headers)
        elif response.status_code == 429:
            raise exceptions.RateLimitException(response.content,
                                                response.content,
                                                response.status_code,
                                                response.headers)
        elif response.status_code in [400, 404]:
            raise exceptions.InvalidRequestException(response.content,
                                                     response.content,
                                                     response.status_code,
                                                     response.headers)
        else:
            raise exceptions.APIException(response.content,
                                          response.content,
                                          response.status_code,
                                          response.headers)

    @classmethod
    def get_class_url(cls):
        '''
        Returns the URI for the resource
        '''
        url = urlparse.urljoin(cls._get_base_url(), cls.resource_url)
        return url

    def get_instance_url(self):
        '''
        Returns the URI for the individual resource
        '''
        url = urlparse.urljoin(self._get_base_url(),
                      '{resource_url}{resource_id}/'.format(
                          resource_url=self.resource_url, resource_id=self.id))
        return url


class ListObject(APIResource):
    '''
    Base HyperTrack list object
    '''
    def __new__(cls, object_class, **kwargs):
        cls.resource_url = object_class.resource_url
        return APIResource.__new__(cls, object_class, **kwargs)

    def __init__(self, object_class, **kwargs):
        '''
        Converts objects in the list to their resource class
        '''
        super(ListObject, self).__init__(**kwargs)
        self._object_class = object_class

        if self.get('results'):
            self.results = [object_class(**obj) for obj in self.results]
        else:
            self.results = []

    def __iter__(self):
        '''
        Allow iteration over the resources in the list
        '''
        return getattr(self, 'results', []).__iter__()

    def list(self, **params):
        '''
        Mixin method to list the resources from the API
        '''
        url = self.get_class_url()
        resp = self._make_request('get', url, params=params)
        return ListObject(self._object_class, **resp.json())

    def next_page(self):
        '''
        Returns a list object for the next page
        '''
        if self.get('next'):
            querystring = urlparse.urlparse(self.next).query
            params = dict(urlparse.parse_qsl(querystring))
            return self.list(**params)
        else:
            # TODO: Should we raise exception here?
            return self.__class__(self._object_class)

    def previous_page(self):
        '''
        Returns a list object for the previous page
        '''
        if self.get('previous'):
            querystring = urlparse.urlparse(self.previous).query
            params = dict(urlparse.parse_qsl(querystring))
            return self.list(**params)
        else:
            # TODO: Should we raise exception here?
            return self.__class__(self._object_class)


class CreateMixin(object):
    '''
    Mixin to allow resources to be created on the API
    '''
    @classmethod
    def create(cls, files=None, **data):
        '''
        Mixin method to create the resource on the API
        '''
        url = cls.get_class_url()
        resp = cls._make_request('post', url, data=data, files=files)
        return cls(**resp.json())


class RetrieveMixin(object):
    '''
    Mixin to allow a resource to be retrieved from the API
    '''
    @classmethod
    def retrieve(cls, hypertrack_id):
        '''
        Mixin method to retrieve the resource from the API
        '''
        url = urlparse.urljoin(cls._get_base_url(),
                      '{resource_url}{resource_id}/'.format(
                          resource_url=cls.resource_url,
                          resource_id=hypertrack_id))
        resp = cls._make_request('get', url)
        return cls(**resp.json())


class ListMixin(object):
    '''
    Mixin to allow resources to be listed from the API
    '''
    @classmethod
    def list(cls, **params):
        '''
        Mixin method to list the resources from the API
        '''
        url = cls.get_class_url()
        resp = cls._make_request('get', url, params=params)
        return ListObject(cls, **resp.json())


class UpdateMixin(object):
    '''
    Mixin to allow a resource to be updated on the API
    '''
    def save(self, files=None):
        '''
        Mixin method to update the resource on the API
        '''
        url = self.get_instance_url()
        data = dict([(k, getattr(self, k)) for k in self._unsaved_keys])
        resp = self._make_request('patch', url, data=data, files=files)
        self._unsaved_keys = set()
        return self.__class__(**resp.json())


class DeleteMixin(object):
    '''
    Mixin to allow a resource to be deleted on the API
    '''
    def delete(self):
        '''
        Mixin method to update the resource on the API
        '''
        url = self.get_instance_url()
        resp = self._make_request('delete', url)
        return self


class Customer(APIResource, CreateMixin, RetrieveMixin, UpdateMixin, ListMixin):
    '''
    The Customer Resource: http://docs.hypertrack.io/docs/customers
    '''
    resource_url = 'customers/'


class Destination(APIResource, CreateMixin, RetrieveMixin, UpdateMixin,
                  ListMixin):
    '''
    The Destination Resource: http://docs.hypertrack.io/docs/destinations
    '''
    resource_url = 'destinations/'


class Fleet(APIResource, CreateMixin, RetrieveMixin, UpdateMixin, ListMixin):
    '''
    The Fleet Resource: http://docs.hypertrack.io/docs/fleets
    '''
    resource_url = 'fleets/'


class Driver(APIResource, CreateMixin, RetrieveMixin, UpdateMixin, ListMixin):
    '''
    The Driver Resource: http://docs.hypertrack.io/docs/drivers
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

    def save(self, *args, **kwargs):
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
    The Hub Resource: http://docs.hypertrack.io/docs/hubs
    '''
    resource_url = 'hubs/'


class Task(APIResource, CreateMixin, RetrieveMixin, UpdateMixin, ListMixin):
    '''
    The Task Resource: http://docs.hypertrack.io/docs/tasks
    '''
    resource_url = 'tasks/'

    def complete(self, **data):
        url = urlparse.urljoin(self.get_instance_url(), 'completed/')
        resp = self._make_request('post', url, data=data)
        return self.__class__(**resp.json())


class Trip(APIResource, CreateMixin, RetrieveMixin, UpdateMixin, ListMixin):
    '''
    The Trip Resource: http://docs.hypertrack.io/docs/trips
    '''
    resource_url = 'trips/'

    def end(self, **data):
        url = urlparse.urljoin(self.get_instance_url(), 'end/')
        resp = self._make_request('post', url, data=data)
        return self.__class__(**resp.json())


class GPSLog(APIResource, CreateMixin, RetrieveMixin, ListMixin):
    '''
    The GPS Resource: http://docs.hypertrack.io/docs/gps-logs
    '''
    resource_url = 'gps/'

    @classmethod
    def filtered(cls, **params):
        url = urlparse.urljoin(cls.get_class_url(), 'filtered/')
        resp = cls._make_request('get', url, params=params)
        return ListObject(cls, **resp.json())


class Event(APIResource, RetrieveMixin, ListMixin):
    '''
    The Event Resource: http://docs.hypertrack.io/docs/events
    '''
    resource_url = 'events/'
