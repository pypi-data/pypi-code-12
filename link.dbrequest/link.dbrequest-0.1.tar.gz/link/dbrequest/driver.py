# -*- coding: utf-8 -*-

from b3j0f.conf import Configurable, category
from link.middleware.core import Middleware
from link.dbrequest import CONF_BASE_PATH

from link.dbrequest.comparison import C
from link.dbrequest.assignment import A
from link.dbrequest.ast import AST


@Configurable(
    paths='{0}/driver.conf'.format(CONF_BASE_PATH),
    conf=category('DRIVER')
)
class Driver(Middleware):

    __protocols__ = ['storage']

    QUERY_COUNT = 'count'
    QUERY_CREATE = 'save'
    QUERY_READ = 'find'
    QUERY_UPDATE = 'update'
    QUERY_DELETE = 'delete'

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

        return Model(self, result)

    def find_elements(self, ast):
        result = self._process_query(self.conn, {
            'type': Driver.QUERY_READ,
            'filter': ast
        })

        return [
            Model(self, item)
            for item in result
        ]

    def update_elements(self, filter_ast, update_ast):
        result = self._process_query(self.conn, {
            'type': Driver.QUERY_UPDATE,
            'filter': filter_ast,
            'update': update_ast
        })

        return [
            Model(self, item)
            for item in result
        ]

    def remove_elements(self, ast):
        return self._process_query(self.conn, {
            'type': Driver.QUERY_DELETE,
            'filter': ast
        })


class Model(object):
    def __init__(self, driver, data, *args, **kwargs):
        super(Model, self).__init__(*args, **kwargs)

        self.driver = driver
        self.data = data

    def _get_filter(self):
        condition = None

        for key, val in self.data.items():
            if condition is None:
                condition = C(key) == val

            else:
                condition = condition & (C(key) == val)

        return condition

    def _get_update(self):
        return [
            A(key, val).get_ast()
            for key, val in self.data.items()
        ]

    def save(self):
        assignments = self._get_update()
        self.result = self.driver.put_element(assignments)

    def delete(self):
        condition = self._get_filter()

        self.driver.remove_elements([
            AST('filter', condition.get_ast())
        ])

    def __getitem__(self, prop):
        return self.data[prop]

    def __setitem__(self, prop, val):
        self.data[prop] = val

    def __delitem__(self, prop):
        del self.data[prop]

    def __getattr__(self, prop):
        return self.data[prop]

    def __setattr__(self, prop, val):
        self.data[prop] = val

    def __delattr__(self, prop):
        del self.data[prop]
