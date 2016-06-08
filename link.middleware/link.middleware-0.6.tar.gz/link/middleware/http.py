# -*- coding: utf-8 -*-

from b3j0f.conf import Configurable, category

from link.middleware.core import Middleware
from link.middleware import CONF_BASE_PATH
import requests


@Configurable(
    paths='{0}/http.conf'.format(CONF_BASE_PATH),
    conf=category('HTTP')
)
class HTTPMiddleware(Middleware):
    """
    HTTP middleware.
    """

    __protocols__ = ['http']

    class Error(Exception):
        """
        Error class raised by middleware methods.
        """

        pass

    def get(self):
        """
        GET document pointed by middleware.

        :returns: document's content
        :rtype: str
        """

        response = requests.get(self.tourl())

        if not response.ok:
            raise HTTPMiddleware.Error(response.text)

        return response.text

    def post(self, data):
        """
        POST data to document pointed by middleware.

        :param data: data used by POST
        :type data: dict

        :returns: request response's content
        :rtype: str
        """

        response = requests.post(self.tourl(), data=data)

        if not response.ok:
            raise HTTPMiddleware.Error(response.text)

        return response.text

    def put(self, data):
        """
        PUT data to document pointed by middleware.

        :param data: data used by PUT
        :type data: dict

        :returns: request response's content
        :rtype: str
        """

        response = requests.put(self.tourl(), data=data)

        if not response.ok:
            raise HTTPMiddleware.Error(response.text)

        return response.text

    def delete(self, data):
        """
        DELETE document pointed by middleware.

        :param data: data used for DELETE request
        :type data: dict

        :returns: request response's content
        :rtype: str
        """

        response = requests.delete(self.tourl(), data=data)

        if not response.ok:
            raise HTTPMiddleware.Error(response.text)

        return response.text

    def options(self):
        """
        Check allowed requests on document pointed by middleware.

        :returns: list of allowed requests
        :rtype: list
        """

        response = requests.options(self.tourl())

        if not response.ok:
            raise HTTPMiddleware.Error(response.text)

        return response.headers['allow']

    def head(self):
        """
        Get headers of document pointed by middleware.

        :returns: headers
        :rtype: dict
        """

        response = requests.head(self.tourl())

        if not response.ok:
            raise HTTPMiddleware.Error(response.text)

        return response.headers

    def patch(self, data):
        """
        PATCH document pointed by middleware.

        :param data: data used for PATCH request
        :type data: dict

        :returns: request response's content
        :rtype: str
        """

        response = requests.patch(self.tourl(), data=data)

        if not response.ok:
            raise HTTPMiddleware.Error(response.text)

        return response.text
