import uuid

from . import utils
from .api import Api
from .exceptions import ResourceNotFound


class Resource(object):
    """Base class for all REST services
    """
    convert_resources = {}
    ensure_query_projections = {}

    def __init__(self, attributes=None):
        attributes = attributes or {}
        self.__dict__['api'] = Api.Default()

        super(Resource, self).__setattr__('__data__', {})
        super(Resource, self).__setattr__('error', None)
        super(Resource, self).__setattr__('headers', {})
        super(Resource, self).__setattr__('header', {})
        super(Resource, self).__setattr__('request_id', None)
        self.merge(attributes)

    @staticmethod
    def _ensure_projections(params, extra_projections):
        """Ensures that if projections are given in the params, they contain the given ones.

        Only works when `params['projection']` exists and is a dict.

        @param params: URL parameters
        @type params: dict
        @param extra_projections: extra projections to add
        @type extra_projections: dict
        """

        if not extra_projections:
            return

        try:
            if isinstance(params['projection'], dict):
                params['projection'].update(extra_projections)
        except (TypeError, KeyError):
            # Either params is None or params['projection'] doesn't exist.
            pass

    def generate_request_id(self):
        """Generate unique request id
        """
        if self.request_id is None:
            self.request_id = str(uuid.uuid4())
        return self.request_id

    def http_headers(self):
        """Generate HTTP header
        """
        return utils.merge_dict(self.header, self.headers,
            {'Pillar-Request-Id': self.generate_request_id()})

    def __str__(self):
        return self.__data__.__str__()

    def __repr__(self):
        return self.__data__.__str__()

    def __getattr__(self, name):
        return self.__data__.get(name)

    def __contains__(self, item):
        return item in self.__data__

    def __setattr__(self, name, value):
        try:
            # Handle attributes(error, header, request_id)
            super(Resource, self).__getattribute__(name)
            super(Resource, self).__setattr__(name, value)
        except AttributeError:
            self.__data__[name] = self.convert(name, value)

    def success(self):
        return self.error is None

    def merge(self, new_attributes):
        """Merge new attributes e.g. response from a post to Resource
        """
        for key, val in new_attributes.items():
            setattr(self, key, val)

    def convert(self, name, value):
        """Convert the attribute values to configured class
        """
        if isinstance(value, dict):
            cls = self.convert_resources.get(name, Resource)
            return cls(value)
        elif isinstance(value, list):
            new_list = []
            for obj in value:
                new_list.append(self.convert(name, obj))
            return new_list
        else:
            return value

    def __getitem__(self, key):
        return self.__data__[key]

    def __setitem__(self, key, value):
        self.__data__[key] = self.convert(key, value)

    def to_dict(self):

        def parse_object(value):
            if isinstance(value, Resource):
                return value.to_dict()
            elif isinstance(value, list):
                new_list = []
                for obj in value:
                    new_list.append(parse_object(obj))
                return new_list
            else:
                return value

        data = {}
        for key in self.__data__:
            data[key] = parse_object(self.__data__[key])
        return data

    def from_dict(self, d):
        for key, val in d.iteritems():
            self[key] = val
        return self


class Find(Resource):

    @classmethod
    def find(cls, resource_id, params=None, api=None):
        """Locate resource, usually using ObjectID

        Usage::

            >>> Node.find("507f1f77bcf86cd799439011")
        """

        api = api or Api.Default()

        url = utils.join_url(cls.path, str(resource_id))
        if params is not None:
            cls._ensure_projections(params, cls.ensure_query_projections)
            url = utils.join_url_params(url, params)

        item = utils.convert_datetime(api.get(url))
        return cls(item)

    @classmethod
    def find_first(cls, params, api=None):
        """Get list of resources, allowing some parameters such as:
        - count
        - start_time
        - sort_by
        - sort_order

        Usage::

            >>> shots = Nodes.all({'count': 2, 'type': 'shot'})
        """
        api = api or Api.Default()

        # Force delivery of only 1 result
        params['max_results'] = 1
        cls._ensure_projections(params, cls.ensure_query_projections)
        url = utils.join_url_params(cls.path, params)

        response = api.get(url)
        res = cls(response)
        if res._items:
            return utils.convert_datetime(res._items[0])
        else:
            return None

    @classmethod
    def find_one(cls, params, api=None):
        """Get one resource starting from parameters different than the resource
        id. TODO if more than one match for the query is found, raise exception.
        """
        api = api or Api.Default()

        # Force delivery of only 1 result
        params['max_results'] = 1
        cls._ensure_projections(params, cls.ensure_query_projections)
        url = utils.join_url_params(cls.path, params)

        response = api.get(url)
        # Keep the response a dictionary, and cast it later into an object.
        if '_items' in response:
            return cls(utils.convert_datetime(response['_items'][0]))
        else:
            raise ResourceNotFound(response)


class List(Resource):

    # Class of the list result itself.
    list_class = Resource

    @classmethod
    def all(cls, params=None, api=None):
        """Get list of resources, allowing some parameters such as:
        - count
        - start_time
        - sort_by
        - sort_order

        Usage::

            >>> shots = Nodes.all({'count': 2, 'type': 'shot'})
        """

        return cls.all_from_endpoint(cls.path, params=params, api=api)

    @classmethod
    def all_from_endpoint(cls, endpoint_url, params=None, api=None):
        """Retrieves a list of resources from a custom endpoint."""

        api = api or Api.Default()

        if params is None:
            url = endpoint_url
        else:
            cls._ensure_projections(params, cls.ensure_query_projections)
            url = utils.join_url_params(endpoint_url, params)

        response = api.get(url)

        if '_items' in response:
            items = response['_items']
            for idx, item in enumerate(items):
                items[idx] = cls(utils.convert_datetime(item))
            return cls.list_class(response)

        # To handle the case when response is JSON Array
        if isinstance(response, list):
            new_resp = [cls(elem) for elem in response]
            return new_resp

        # Fall back to just returning the response.
        return response


class Create(Resource):

    def create(self, api=None):
        """Create a resource

        Usage::

            >>> node = Node({})
            >>> node.create()
        """

        api = api or self.api
        headers = self.http_headers()
        attributes = utils.remove_none_attributes(self.to_dict())
        new_attributes = api.post(self.path, attributes, headers)
        self.error = None
        self.merge(new_attributes)
        return self.success()


class Update(Resource):
    """Update a resource
    """

    def update(self, attributes=None, api=None):
        api = api or self.api
        attributes = attributes or self.to_dict()
        etag = attributes['_etag']
        attributes.pop('_id')
        attributes.pop('_etag')
        attributes.pop('_created')
        attributes.pop('_updated')
        attributes.pop('_links', None)
        attributes.pop('_deleted', None)
        attributes = utils.remove_none_attributes(attributes)
        url = utils.join_url(self.path, str(self['_id']))
        headers = utils.merge_dict(
            self.http_headers(),
            {'If-Match': str(etag)})
        new_attributes = api.put(url, attributes, headers)
        self.error = None
        self.merge(new_attributes)
        return self.success()


class Replace(Resource):
    """Partial update or modify resource
    see http://williamdurand.fr/2014/02/14/please-do-not-patch-like-an-idiot/

    Usage::

        >>> node = Node.find("507f1f77bcf86cd799439011")
        >>> node.replace([{'op': 'replace', 'path': '/name', 'value': 'Renamed Shot 2' }])
    """

    def replace(self, attributes=None, files=None, api=None):
        api = api or self.api
        attributes = attributes or self.to_dict()
        etag = attributes['_etag']
        attributes.pop('_id')
        attributes.pop('_etag')
        attributes.pop('_created')
        attributes.pop('_updated')
        attributes.pop('_links', None)
        attributes.pop('_deleted', None)
        if 'parent' in attributes:
            attributes.pop('parent')
        url = utils.join_url(self.path, str(self['_id']))
        headers = utils.merge_dict(
            self.http_headers(),
            {'If-Match': str(etag)})
        new_attributes = api.patch(url, attributes, headers, files)
        self.error = None
        self.merge(new_attributes)
        return self.success()


class Delete(Resource):

    def delete(self, api=None):
        """Delete a resource

        Usage::

            >>> node = Node.find("507f1f77bcf86cd799439011")
            >>> node.delete()
        """
        api = api or self.api
        url = utils.join_url(self.path, str(self['_id']))
        etag = self['_etag']
        headers = {'If-Match': str(etag)}
        new_attributes = api.delete(url, headers)
        self.error = None
        self.merge(new_attributes)
        return self.success()


class Post(Resource):

    def post(self, attributes=None, files=None, api=None):
        """Constructs url with passed in headers and makes post request via
        post method in api class.
        """
        api = api or self.api
        attributes = attributes or {}
        url = utils.join_url(self.path)
        """if not isinstance(attributes, Resource):
            attributes = Resource(attributes, api=self.api)"""
        #files = files or {}
        attributes = utils.remove_none_attributes(attributes)
        new_attributes = api.post(url, attributes, {}, files)
        """if isinstance(cls, Resource):
            cls.error = None
            cls.merge(new_attributes)
            return self.success()
        else:
            return cls(new_attributes, api=self.api)"""
        self.merge(new_attributes)
        return self.success()
