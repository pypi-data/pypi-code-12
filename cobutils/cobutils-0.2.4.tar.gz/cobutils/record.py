#!/usr/bin/python


class Record(dict):
    def __init__(self, definition, data=None, sql=False):
        self.definition = definition
        self._data = data
        if data:
            self.update(definition.extract(data, sql=sql))

    def __getattr__(self, name):
        if name in self:
            return self[name]
        raise AttributeError(name)

    def get_bytes(self):
        return self.definition.get_bytes(self)

    def get_fields(self, fields=None):
        if fields == None:
            fields = self.definition.fieldnames()
        return tuple(self[field] for field in fields)
