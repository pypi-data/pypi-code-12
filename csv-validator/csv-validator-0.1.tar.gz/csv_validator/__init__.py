import csv
import collections

from .fields import Field
from .exceptions import ValidationError


class ValidationMetaclass(type):

    @classmethod
    def __prepare__(self, name, bases):
        return collections.OrderedDict()

    def __new__(cls, name, bases, dct):
        subclass = type.__new__(cls, name, bases, dct)

        subclass._fieldnames = []
        subclass._fields = {}
        for key, value in dct.items():
            if isinstance(value, Field):
                subclass._fields[key] = value
                subclass._fieldnames.append(key)
        return subclass


class DictReader(csv.DictReader, metaclass=ValidationMetaclass):

    def __init__(self, *args, capture_errors=False, **kwargs):
        super().__init__(*args, **kwargs)

        self.capture_errors = capture_errors
        self.errors = {}

    @property
    def fieldnames(self):
        return self.__class__._fieldnames

    def __next__(self):
        row = next(self.reader)

        # Skip the first row if it's headers...
        if self.line_num == 0 and row == self.fieldnames:
            row = next(self.reader)

        # unlike the basic reader, we prefer not to return blanks,
        # because we will typically wind up with a dict full of None
        # values
        while row == []:
            row = next(self.reader)
        d = dict(zip(self.fieldnames, row))

        lf = len(self.fieldnames)
        lr = len(row)
        if lf < lr:
            d[self.restkey] = row[lf:]
        elif lf > lr:
            for key in self.fieldnames[lr:]:
                d[key] = self.restval

        for name, field in self._fields.items():
            try:
                d[name] = field.to_python(d[name])
            except ValidationError as e:
                if not self.capture_errors:
                    raise e

                if self.line_num not in self.errors:
                    self.errors[self.line_num] = {'data': row, 'errors': {}}

                self.errors[self.line_num]['errors'][name] = str(e)

        self.line_num = self.reader.line_num

        return d
