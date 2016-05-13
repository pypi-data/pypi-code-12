from __future__ import absolute_import

from itertools import islice

from .exceptions import translate_exceptions, InterfaceError


class Cursor(object):
    def __init__(self, impl):
        self.impl = impl
        self.rowcount = -1
        self.arraysize = 1

    def __iter__(self):
        return self

    def next(self):
        element = self.fetchone()
        if element is None:
            raise StopIteration
        else:
            return element

    def _assert_valid(self):
        if self.impl is None:
            raise InterfaceError("Cursor already closed")

    @property
    def description(self):
        info = self.impl.get_result_set_info()
        if len(info) == 0:
            return None
        else:
            return [(c['name'], c['type_code'], None, None, None, None, c['supports_null_values']) for c in info]

    @translate_exceptions
    def execute(self, sql, parameters=None):
        """Execute an SQL query"""
        self._assert_valid()
        self.impl.prepare(sql)
        if parameters:
            self.impl.add_parameter_set(parameters)
        self.impl.execute()
        self.rowcount = self.impl.get_row_count()

    @translate_exceptions
    def executemany(self, sql, parameters=None):
        """Execute an SQL query"""
        self._assert_valid()
        self.impl.prepare(sql)

        if parameters:
            for parameter_set in parameters:
                self.impl.add_parameter_set(parameter_set)

        self.impl.execute()
        self.rowcount = self.impl.get_row_count()

    @translate_exceptions
    def fetchone(self):
        self._assert_valid()
        result = self.impl.fetchone()
        if len(result) == 0:
            return None 
        else:
            return result  

    @translate_exceptions    
    def fetchall(self):
        return [row for row in self]

    @translate_exceptions    
    def fetchmany(self, size=None):
        if size is None:
            size = self.arraysize
        if (size <= 0):
            raise InterfaceError("Invalid arraysize {} for fetchmany()".format(size))

        return [row for row in islice(self, size)]

    def close(self):
        self.impl = None

    def setinputsizes(self, sizes):
        """
        setinputsizes() has no effect. turbodbc automatically picks appropriate
        return types and sizes. Method exists since PEP-249 requires it.
        """
        pass

    def setoutputsize(self, size, column=None):
        """
        setoutputsize() has no effect. turbodbc automatically picks appropriate
        input types and sizes. Method exists since PEP-249 requires it.
        """
        pass
