# -*- coding: utf-8 -*-

from b3j0f.conf import Configurable, category
from link.middleware.connectable import ConnectableMiddleware
from link.dbrequest.model import Model, Cursor
from link.dbrequest import CONF_BASE_PATH


@Configurable(
    paths='{0}/driver.conf'.format(CONF_BASE_PATH),
    conf=category('DRIVER')
)
class Driver(ConnectableMiddleware):
    """
    Abstract storage driver middleware.
    """

    __protocols__ = ['storage']

    QUERY_COUNT = 'count'
    QUERY_CREATE = 'save'
    QUERY_READ = 'find'
    QUERY_UPDATE = 'update'
    QUERY_DELETE = 'delete'

    model_class = Model
    cursor_class = Cursor

    def _process_query(self, conn, query):
        """
        This method must be overriden, handles every query made to the storage.

        :param conn: storage's connection
        :type conn: as returned by ``_connect()``

        :param query: query to process
        :type query: dict

        :returns: driver's response.
        """

        raise NotImplementedError()

    def count_elements(self, ast):
        """
        Count number of elements matching the query described by the AST.

        :param ast: AST describing the query
        :type ast: list or dict

        :returns: number of elements matching the query
        :rtype: int
        """

        return self._process_query(self.conn, {
            'type': Driver.QUERY_COUNT,
            'filter': ast
        })

    def put_element(self, ast):
        """
        Put element into the store.

        :param ast: AST describing the element to insert
        :type ast: list

        :returns: Inserted element
        :rtype: Model
        """

        result = self._process_query(self.conn, {
            'type': Driver.QUERY_CREATE,
            'update': ast
        })

        return self.model_class(self, result)

    def find_elements(self, ast):
        """
        Find elements matching the query described by the AST.

        :param ast: AST describing the query
        :type ast: list or dict

        :returns: Cursor on matching elements
        :rtype: Cursor
        """

        result = self._process_query(self.conn, {
            'type': Driver.QUERY_READ,
            'filter': ast
        })

        return self.cursor_class(self, result)

    def update_elements(self, filter_ast, update_ast):
        """
        Update elements matching the query described by the AST.

        :param filter_ast: AST describing the query
        :type filter_ast: list

        :param update_ast: AST describing the update
        :type update_ast: list

        :returns: Number of elements modified
        :rtype: int
        """

        return self._process_query(self.conn, {
            'type': Driver.QUERY_UPDATE,
            'filter': filter_ast,
            'update': update_ast
        })

    def remove_elements(self, ast):
        """
        Delete elements matching the query described by the AST.

        :param ast: AST describing the query
        :type ast: list or dict

        :returns: Number of elements deleted
        :rtype: int
        """

        return self._process_query(self.conn, {
            'type': Driver.QUERY_DELETE,
            'filter': ast
        })
