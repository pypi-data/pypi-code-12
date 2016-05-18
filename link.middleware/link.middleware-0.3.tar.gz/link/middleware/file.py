# -*- coding: utf-8 -*-

from b3j0f.conf import Configurable, category
from b3j0f.middleware.url import URLMiddleware

from link.middleware import CONF_BASE_PATH

import os


@Configurable(
    paths='{0}/file.conf'.format(CONF_BASE_PATH),
    conf=category('FILE')
)
class FileMiddleware(URLMiddleware):
    """
    Middleware with the same API as the
    :class:`link.middleware.http.HTTPMiddleware` but with ``file://` URI.
    """

    __protocols__ = ['file']

    def get(self):
        """
        Get content of file pointed by middleware.

        :returns: file's content
        :rtype: str
        """

        with open(self.path) as f:
            result = f.read()

        return result

    def post(self, data):
        """
        Write data to file pointed by middleware.

        :param data: data to write
        :type data: str
        """

        self.put(data)

    def put(self, data):
        """
        Write data to file pointed by middleware.

        :param data: data to write
        :type data: str
        """

        with open(self.path, 'w') as f:
            f.write(data)

    def delete(self, data):
        """
        Delete file pointed by middleware.

        :param data: unused (only for API compatibility)
        """

        if os.path.exists(self.path):
            os.remove(self.path)

    def options(self):
        raise NotImplementedError('Unsupported by protocol')

    def head(self):
        raise NotImplementedError('Unsupported by protocol')

    def patch(self, data):
        raise NotImplementedError('Unsupported by protocol')
