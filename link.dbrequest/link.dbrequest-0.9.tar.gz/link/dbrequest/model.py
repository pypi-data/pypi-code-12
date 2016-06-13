# -*- coding: utf-8 -*-

from link.dbrequest.comparison import C
from link.dbrequest.assignment import A
from link.dbrequest.ast import AST

from six import Iterator, iteritems
import json


class Model(object):
    """
    Model class encapsulating elements in store.

    :param driver: storage driver
    :type driver: Driver

    :param data: encapsulated data
    :type data: dict
    """

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
        """
        Convert data to filter matching the data.

        :returns: Filter
        :rtype: C or CombinedCondition
        """

        condition = None

        for key, val in iteritems(self.data):
            if condition is None:
                condition = C(key) == val

            else:
                condition = condition & (C(key) == val)

        return condition

    def _get_update(self):
        """
        Convert data to assignments.

        :returns: Assignments
        :rtype: list of A
        """

        return [
            A(key, val)
            for key, val in iteritems(self.data)
        ]

    def save(self):
        """
        Save element into store.

        :returns: Inserted document
        :rtype: Model
        """

        assignments = self._get_update()
        return self.driver.put_element([a.get_ast() for a in assignments])

    def delete(self):
        """
        Delete element from store.
        """

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
        if prop not in self.data:
            return super(Model, self).__getattribute__(prop)

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
    """
    Cursor encapsulating storage driver's cursor or result.

    :param driver: storage driver
    :type driver: Driver

    :param cursor: storage's cursor
    """

    __slots__ = ('_cursor', 'driver')

    def __init__(self, driver, cursor, *args, **kwargs):
        super(Cursor, self).__init__(*args, **kwargs)

        self.driver = driver
        self._cursor = cursor

    @property
    def cursor(self):
        return self._cursor

    def to_model(self, doc):
        """
        Convert raw element to Model.

        :param doc: raw element
        :type doc: dict

        :returns: Element as Model
        :rtype: Model
        """

        return Model(self.driver, doc)

    def __len__(self):
        return len(self.cursor)

    def __next__(self):
        return self.to_model(next(self.cursor))

    def __getitem__(self, index):
        return self.to_model(self.cursor[index])
