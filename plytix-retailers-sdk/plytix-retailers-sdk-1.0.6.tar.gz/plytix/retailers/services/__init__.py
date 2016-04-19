from plytix.retailers.models import validate_id
from plytix.retailers.connection import PlytixRetailersConnection
from plytix.retailers.exceptions import *
from plytix.retailers.fields import *

import json
from requests.exceptions import HTTPError


_DEFAULTS = {
    INPUT_PAGE_LENGTH: 100,
    RESPONSE_METADATA_PAGE: 1
}


class BaseEndpoint(object):
    """ Base model for define services. Stores the connection to the Retailers API.
    """
    _BASE_ENDPOINT = None
    _BASE_ENDPOINT_RESOURCE = None

    def __init__(self, connection):
        if not isinstance(connection, PlytixRetailersConnection):
            raise ClientNotValidError('The connection is not valid.')
        self.connection = connection

    def __repr__(self):  # pragma: no cover
        class_name = self.__class__.__name__
        return '<{}: {} object>'.format(class_name, class_name)

    def _create(self, obj=None, fields=None, endpoint=None, data=None):
        """ Create a resource.
        :param obj: Object to save.
        :param fields: Fields of the object to retrieve.
        :param endpoint: Endpoint.
        :param data: Extra data to send.
        :return: The network response.
        """
        if not data and not obj:
            raise ValueError('No data introduced.')

        if data is None and not obj.is_valid(creating=True):
            raise ValueError('No valid object.')

        qs = {}
        if fields:
            if isinstance(fields, list):
                fields = ','.join(fields)
            qs[INPUT_FIELDS] = fields

        endpoint = endpoint or self._BASE_ENDPOINT
        data = data or obj.to_dict()
        try:
            response = self.connection.post(endpoint, data=json.dumps(data), params=qs)
            return response
        except HTTPError as e:
            status_code = e.response.status_code
            try:
                message = e.response.json()[RESPONSE_MESSAGE]
            except Exception as ex:
                message = u'No error message'

            if status_code == 400:
                raise BadRequestError(message)
            elif status_code == 404:
                raise ResourceNotFoundError(message)
            elif status_code == 500:
                raise BadResponseError(message)
            else:
                raise PlytixRetailersAPIError(message)
        except Exception as e:
            raise e

    def _get(self, id, fields=None, endpoint=None, query_string=None):
        """ Get a resource.
        :param id: Identifier of the resource.
        :param fields: Fields of the object to retrieve.
        :param endpoint: Endpoint.
        :param query_string: Extra parameters to send as query string.
        :return: The network response.
        """
        if id and not validate_id(id):
            raise ValueError('Not a valid ObjectId.')

        qs = {}
        if fields:
            if isinstance(fields, list):
                fields = ','.join(fields)
            qs[INPUT_FIELDS] = fields

        if query_string:
            qs.update(query_string)

        endpoint = endpoint or '{endpoint}/{id}'.format(endpoint=self._BASE_ENDPOINT_RESOURCE, id=id)
        try:
            response = self.connection.get(endpoint, params=qs)
            return response
        except HTTPError as e:
            status_code = e.response.status_code
            try:
                message = e.response.json()[RESPONSE_MESSAGE]
            except Exception as ex:
                message = u'No error message'

            if status_code == 400:
                raise BadRequestError(message)
            elif status_code == 404:
                raise ResourceNotFoundError(message)
            elif status_code == 500:
                raise BadResponseError(message)
            else:
                raise PlytixRetailersAPIError(message)
        except Exception as e:
            raise e

    def _list(self, page=None, page_length=None, fields=None, endpoint=None, sort=None):
        """ Get a list of resources.
        :param page: Page.
        :param page_length:  Items per page.
        :param fields: Fields to retrieve.
        :param endpoint: Endpoint resource.
        :param sort: Field to sort by.
        :return: The network response.
        """
        page = page or _DEFAULTS[RESPONSE_METADATA_PAGE]
        page_length = page_length or _DEFAULTS[INPUT_PAGE_LENGTH]

        qs = {
            RESPONSE_METADATA_PAGE: page,
            INPUT_PAGE_LENGTH: page_length,
        }

        if fields:
            if isinstance(fields, list):
                fields = ','.join(fields)
            qs[INPUT_FIELDS] = fields
        if sort:
            qs[INPUT_SORT] = sort

        endpoint = endpoint or self._BASE_ENDPOINT
        try:
            response = self.connection.get(endpoint, params=qs)
            return response
        except HTTPError as e:
            status_code = e.response.status_code
            try:
                message = e.response.json()[RESPONSE_MESSAGE]
            except Exception as ex:
                message = u'No error message'

            if status_code == 400:
                raise BadRequestError(message)
            elif status_code == 404:
                raise ResourceNotFoundError(message)
            elif status_code == 500:
                raise BadResponseError(message)
            else:
                raise PlytixRetailersAPIError(message)
        except Exception as e:
            raise e

    def _raw_get(self, endpoint, query_string=None):
        if query_string is not None:
            try:
                assert isinstance(query_string, dict)
            except AssertionError as ae:
                raise ValueError('query_string must be a dictionary.')

        try:
            response = self.connection.get(endpoint, params=query_string)
            return response
        except HTTPError as e:
            status_code = e.response.status_code
            try:
                message = e.response.json()[RESPONSE_MESSAGE]
            except Exception as ex:
                message = u'No error message'

            if status_code == 400:
                raise BadRequestError(message)
            elif status_code == 404:
                raise ResourceNotFoundError(message)
            elif status_code == 500:
                raise BadResponseError(message)
            else:
                raise PlytixRetailersAPIError(message)
        except Exception as e:
            raise e

    def _raw_post(self, endpoint, data=None, query_string=None):
        if query_string is not None:
            try:
                assert isinstance(query_string, dict)
            except AssertionError as ae:
                raise ValueError('query_string must be a dictionary.')
        if data is not None:
            try:
                assert isinstance(data, dict)
            except AssertionError as ae:
                    raise ValueError('query_string must be a dictionary.')

        try:
            response = self.connection.post(endpoint, params=query_string, data=json.dumps(data))
            return response
        except HTTPError as e:
            status_code = e.response.status_code
            try:
                message = e.response.json()[RESPONSE_MESSAGE]
            except Exception as ex:
                message = u'No error message'

            if status_code == 400:
                raise BadRequestError(message)
            elif status_code == 404:
                raise ResourceNotFoundError(message)
            elif status_code == 500:
                raise BadResponseError(message)
            else:
                raise PlytixRetailersAPIError(message)
        except Exception as e:
            raise e

    def _search(self, page=None, page_length=None, fields=None, endpoint=None, sort=None, data=None):
        """ Search resources.
        :param page: Page.
        :param page_length:  Items per page.
        :param fields: Fields to retrieve.
        :param endpoint: Endpoint resource.
        :param sort: Field to sort by.
        :param data: Data to send.
        :return: The network response.
        """
        page = page or _DEFAULTS[RESPONSE_METADATA_PAGE]
        page_length = page_length or _DEFAULTS[INPUT_PAGE_LENGTH]

        qs = {
            RESPONSE_METADATA_PAGE: page,
            INPUT_PAGE_LENGTH: page_length,
        }

        if fields:
            if isinstance(fields, list):
                fields = ','.join(fields)
            qs[INPUT_FIELDS] = fields
        if sort:
            qs[INPUT_SORT] = sort

        data = json.dumps(data) if data is not None else None
        endpoint = endpoint or self._BASE_ENDPOINT + '/search'
        try:
            response = self.connection.post(endpoint, params=qs, data=data)
            return response
        except HTTPError as e:
            status_code = e.response.status_code
            try:
                message = e.response.json()[RESPONSE_MESSAGE]
            except Exception as ex:
                message = u'No error message'

            if status_code == 400:
                raise BadRequestError(message)
            elif status_code == 404:
                raise ResourceNotFoundError(message)
            elif status_code == 500:
                raise BadResponseError(message)
            else:
                raise PlytixRetailersAPIError(message)
        except Exception as e:
            raise e

    def _update(self, obj, fields=None, endpoint=None, data=None):
        """ Update a resource.
        :param obj: Object modified.
        :param fields: Fields of the object to retrieve.
        :param endpoint: Endpoint.
        :param data: Data to send.
        :return: The object modified.
        """
        if not obj.is_valid():
            raise ValueError('No valid object.')

        qs = {}
        if fields:
            if isinstance(fields, list):
                fields = ','.join(fields)
            qs[INPUT_FIELDS] = fields

        endpoint = endpoint or '{endpoint}/{id}'.format(endpoint=self._BASE_ENDPOINT_RESOURCE, id=obj.id)
        data = data or json.dumps(obj.to_dict(include_id=False))

        try:
            response = self.connection.put(endpoint, data=data, params=qs)
            return response
        except HTTPError as e:
            status_code = e.response.status_code
            try:
                message = e.response.json()[RESPONSE_MESSAGE]
            except Exception as ex:
                message = u'No error message'

            if status_code == 400:
                raise BadRequestError(message)
            elif status_code == 404:
                raise ResourceNotFoundError(message)
            elif status_code == 500:
                raise BadResponseError(message)
            else:
                raise PlytixRetailersAPIError(message)
        except Exception as e:
            raise e


class ResponseList(object):
    """ Wrapper to add some utilities to Response's lists.
    """
    def __init__(self, items, page, total, total_pages):
        """
        :param items: Response items.
        :param page: Response page.
        :param total: Total items.
        :param total_pages: Total pages.
        :return: A ResponseList instance initialized.
        """
        self._page = page
        self._total = total
        self._total_pages = total_pages
        self._items = items

    def __len__(self):
        """
        :return: The number of items retrieved.
        """
        return len(self._items)

    def __getitem__(self, item):
        return self._items[item]

    def __iter__(self):
        """
        :return: Iterator
        """
        return self._items.__iter__()

    def __repr__(self):  # pragma: no cover
        class_name = self.__class__.__name__
        return '<{}: {} object>'.format(class_name, class_name)

    @property
    def has_more(self):
        """
        :return: True if there are a next page.
        """
        return self.page < self.total_pages

    @property
    def page(self):
        """
        :return: The result's page.
        """
        return self._page

    @property
    def total(self):
        """
        :return: The number of results availables to retrieve. This number differs of the returned by the len() method.
        """
        return self._total

    @property
    def total_pages(self):
        """
        :return: The number of pages availables to retrieve.
        """
        return self._total_pages


class ResponseDict(ResponseList):
    def items(self):
        """
        :return: Return key, value iterator.
        """
        return self._items.items()

    def values(self):
        """
        :return: Return the collection values
        """
        return self._items.values()

    def keys(self):
        """
        :return: Return the collection keys.
        """
        return self._items.keys()