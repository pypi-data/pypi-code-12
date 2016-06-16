# -*- coding: utf-8 -*-


class Field(object):
    def __init__(self, name):
        self.field_name = name
        self.simplex = True

    def is_null(self):
        self.criteria = '(({field} = 0) OR ({field} IS NULL))'.format(field=self.field_name)
        return self

    def is_not_null(self):
        self.criteria = '({field} IS NOT NULL)'.format(field=self.field_name)
        return self

    def in_list(self, lst):
        self.criteria = '({} IN {})'.format(self.field_name, tuple(lst))
        return self

    def __criteria(self, operator, value):
        self.criteria = '({} {} {!r})'.format(self.field_name, operator, value)
        return self

    def __eq__(self, value):
        return self.__criteria('=', value)

    def __lt__(self, value):
        return self.__criteria('<', value)

    def __le__(self, value):
        return self.__criteria('<=', value)

    def __ne__(self, value):
        return self.__criteria('!=', value)

    def __gt__(self, value):
        return self.__criteria('>', value)

    def __ge__(self, value):
        return self.__criteria('>=', value)

    def __and__(self, other):
        fmt = ' AND {}' if other.simplex else ' AND ({:s})'
        self.criteria += fmt.format(other)
        self.simplex = False
        return self

    def __or__(self, other):
        fmt = ' OR {}' if other.simplex else ' OR ({:s})'
        self.criteria += fmt.format(other)
        self.simplex = False
        return self

    def __str__(self):
        return self.criteria
