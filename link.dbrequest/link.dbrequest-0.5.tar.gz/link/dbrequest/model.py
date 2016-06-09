# -*- coding: utf-8 -*-

from link.dbrequest.comparison import C
from link.dbrequest.assignment import A
from link.dbrequest.ast import AST

from collections import Iterator
import json


class Model(object):
    __slots__ = ('driver', 'data')

    def __init__(self, driver, data, *args, **kwargs):
        super(Model, self).__init__(*args, **kwargs)

        self.driver = driver
        self.data = data

    def __str__(self):
        return json.dumps(self.data)

    def __repr__(self):
        return 'Model({0})'.format(json.dumps(self.data))

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
        return self.driver.put_element(assignments)

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

    def __getattribute__(self, prop):
        if prop in ['data', 'driver', '__dict__']:
            return super(Model, self).__getattribute__(prop)

        if prop not in self.data:
            raise AttributeError(
                'No attribute "{0}" found in data'.format(prop)
            )

        return self.data[prop]

    def __setattr__(self, prop, val):
        if prop in ['data', 'driver', '__dict__']:
            super(Model, self).__setattr__(prop, val)

        else:
            self.data[prop] = val

    def __delattr__(self, prop):
        if prop in ['data', 'driver', '__dict__']:
            super(Model, self).__delattr__(prop)

        else:
            del self.data[prop]


class Cursor(Iterator):
    __slots__ = ('_cursor', 'driver')

    def __init__(self, driver, cursor, *args, **kwargs):
        super(Cursor, self).__init__(*args, **kwargs)

        self.driver = driver
        self._cursor = cursor

    @property
    def cursor(self):
        return self._cursor

    def to_model(self, doc):
        return Model(self.driver, doc)

    def __len__(self):
        return len(self.cursor)

    def next(self):
        return self.to_model(self.cursor.next())

    def __getitem__(self, index):
        return self.to_model(self.cursor[index])
