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

    __protocols__ = ['storage']

    QUERY_COUNT = 'count'
    QUERY_CREATE = 'save'
    QUERY_READ = 'find'
    QUERY_UPDATE = 'update'
    QUERY_DELETE = 'delete'

    model_class = Model
    cursor_class = Cursor

    def _process_query(self, conn, query):
        raise NotImplementedError()

    def count_elements(self, ast):
        return self._process_query(self.conn, {
            'type': Driver.QUERY_COUNT,
            'filter': ast
        })

    def put_element(self, ast):
        result = self._process_query(self.conn, {
            'type': Driver.QUERY_CREATE,
            'update': ast
        })

        return self.model_class(self, result)

    def find_elements(self, ast):
        result = self._process_query(self.conn, {
            'type': Driver.QUERY_READ,
            'filter': ast
        })

        return self.cursor_class(self, result)

    def update_elements(self, filter_ast, update_ast):
        return self._process_query(self.conn, {
            'type': Driver.QUERY_UPDATE,
            'filter': filter_ast,
            'update': update_ast
        })

    def remove_elements(self, ast):
        return self._process_query(self.conn, {
            'type': Driver.QUERY_DELETE,
            'filter': ast
        })
