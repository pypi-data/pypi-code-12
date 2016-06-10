import json
from datetime import datetime, timezone, timedelta
from decimal import Decimal

import pytest
from frozendict import frozendict
from . import dumps, loads, PhunticUnknownTypeError, wraps, unwraps


class MyTestClass:
    pass


class AssertFuncMixin:
    def assertFunc(self, obj, expected):
        raise NotImplementedError()


class PhunticTestCases(AssertFuncMixin):
    def test_none(self):
        s = dumps(None, sort_keys=True)
        assert s == json.dumps({"_type": "none"}, sort_keys=True)
        assert loads(s) is None

    def test_string(self):
        obj = 'test'
        self.assertFunc(obj, {"_type": "str", "value": obj})

    def test_int(self):
        obj = 100500
        self.assertFunc(obj, {"_type": "int", "value": obj})

    def test_float(self):
        obj = 3.1428
        self.assertFunc(obj, {"_type": "float", "value": obj})

        obj = float(1)
        self.assertFunc(obj, {"_type": "float", "value": obj})
        s = dumps(obj, sort_keys=True)
        assert isinstance(loads(s), float)

    def test_bool(self):
        self.assertFunc(True, {"_type": "bool", "value": True})
        self.assertFunc(False, {"_type": "bool", "value": False})

    def test_list(self):
        obj = []
        self.assertFunc(obj, {"_type": "list", "value": []})

        obj = [1, 2, 3]
        expected = {
            "_type": "list",
            "value": [
                {"_type": "int", "value": 1},
                {"_type": "int", "value": 2},
                {"_type": "int", "value": 3},
            ]
        }
        self.assertFunc(obj, expected)

    def test_set(self):
        obj = set()
        self.assertFunc(obj, {"_type": "set", "value": []})

        obj = {1, 2}
        expected = {
            "_type": "set",
            "value": [
                {"_type": "int", "value": 1},
                {"_type": "int", "value": 2},
            ]
        }
        self.assertFunc(obj, expected)

    def test_frozenset(self):
        obj = frozenset()
        self.assertFunc(obj, {"_type": "frozenset", "value": []})

        obj = frozenset([1, 2])
        expected = {
            "_type": "frozenset",
            "value": [
                {"_type": "int", "value": 1},
                {"_type": "int", "value": 2}
            ]
        }
        self.assertFunc(obj, expected)

    def test_tuple(self):
        obj = tuple()
        self.assertFunc(obj, {"_type": "tuple", "value": []})

        obj = ('test', 1, 1.12)
        expected = {
            "_type": "tuple",
            "value": [
                {"_type": "str", "value": "test"},
                {"_type": "int", "value": 1},
                {"_type": "float", "value": 1.12},
            ]
        }
        self.assertFunc(obj, expected)

    def test_dict(self):
        obj = dict()
        self.assertFunc(obj, {"_type": "dict", "value": {}})

        obj = {'one': 'test', 'two': 123}
        expected = {
            "_type": "dict",
            "value": {
                "one": {
                    "_type": "str",
                    "value": "test",
                },
                "two": {
                    "_type": "int",
                    "value": 123,
                }
            }
        }
        self.assertFunc(obj, expected)

    def test_frozendict(self):
        obj = frozendict()
        self.assertFunc(obj, {"_type": "frozendict", "value": {}})

        obj = frozendict(one='test', three=3.14)
        expected = {
            "_type": "frozendict",
            "value": {
                "one": {
                    "_type": "str",
                    "value": "test",
                },
                "three": {
                    "_type": "float",
                    "value": 3.14,
                }
            }
        }
        self.assertFunc(obj, expected)

    def test_decimal(self):
        obj = Decimal('1.2342')
        self.assertFunc(obj, {"_type": "decimal", "value": str(obj)})

    def test_datetime(self):
        obj = datetime.now()
        obj -= timedelta(microseconds=obj.microsecond)
        self.assertFunc(obj, {"_type": "datetime", "value": obj.replace(tzinfo=timezone.utc).timestamp()})


class TestPhunticJson(PhunticTestCases):
    def assertFunc(self, obj, expected):
        s = dumps(obj, sort_keys=True)
        assert s == json.dumps(expected, sort_keys=True)
        assert loads(s) == obj

    def test_class(self):
        obj = object()
        with pytest.raises(PhunticUnknownTypeError):
            dumps(obj)

    def test_custom_class(self):
        obj = MyTestClass()
        with pytest.raises(PhunticUnknownTypeError):
            dumps(obj)

    def test_func(self):
        obj = lambda x: x
        with pytest.raises(PhunticUnknownTypeError):
            dumps(obj)

    def test_decode_unknown(self):
        data = json.dumps({'_type': 'fuck', 'value': 1})
        with pytest.raises(ValueError):
            loads(data)


class TestPhunticWrap(PhunticTestCases):
    def assertFunc(self, obj, expected):
        wrapped = wraps(obj)
        assert wrapped == expected
        assert unwraps(wrapped) == obj
