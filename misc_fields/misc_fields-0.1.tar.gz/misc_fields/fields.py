from collections import defaultdict
from enum import Enum
from typing import List, Callable

from peewee import TextField


# from utils import CaseInsensitiveDict
#
#
# class XmlDictField(TextField):
#     def python_value(self, value):
#         return CaseInsensitiveDict.FromXML(value)
#
#     def db_value(self, value):
#         return CaseInsensitiveDict(value).XML()


class EnumField(TextField):
    def __init__(self, enum_type, default_enum=0, *args, **kwargs):
        super(EnumField, self).__init__(*args, **kwargs)
        self.enum_type = enum_type
        self.default_enum = default_enum
        pass

    def python_value(self, value):
        return self.enum_type(int(value) or self.default_enum)

    def db_value(self, value: Enum):
        if value is None:
            return None
        return value.value


class StrategyField(TextField):
    members = None

    def __init__(self, members: List[Callable], default_strategy=None, *args, **kwargs):
        super(StrategyField, self).__init__(*args, **kwargs)
        self.strategies = defaultdict(lambda: default_strategy, **dict(map(lambda f: (f.__name__, f), members)))

    def python_value(self, value):
        return self.strategies[value]

    def db_value(self, value: Callable):
        if value is None:
            return None
        if value.__name__ not in self.strategies:
            raise LookupError("field " + self.name + " contains no method " + value.__name__)
        return value.__name__
