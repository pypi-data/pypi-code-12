# coding: utf-8

import simplejson
from pkg_resources import resource_string
from ._compat import unicode_type
from .utils import bisect_search_right


__all__ = ['Division']


class DivisionLevel(object):
    country = 'country'
    province = 'province'
    prefecture = 'prefecture'
    county = 'county'
    township = 'township'


class Division(object):
    _division_tree = []
    _jd_division_mappings = simplejson.loads(resource_string(__name__, 'data/jd_division_mappings.json'))
    _jd_division = simplejson.loads(resource_string(__name__, 'data/jd_division.json'))
    version = ''

    @classmethod
    def _traverse(cls, code, l):
        index = bisect_search_right(l, code, key=lambda x: x[0])
        if index == 0:
            return None

        return l[index-1]

    @classmethod
    def get_name(cls, code):
        l = cls._division_tree
        while l:
            record = cls._traverse(code, l)
            if not record:
                return None

            if record[0] == code:
                return record[1]

            l = record[2]

    @classmethod
    def get_stack(cls, code):
        code = unicode_type(code)
        l = cls._division_tree
        stack = []

        while l:
            record = cls._traverse(code, l)
            if not record:
                return stack
            stack.append(record[:2])
            l = record[2]
        return stack

    @classmethod
    def traverse(cls, code):
        code = unicode_type(code)
        l = cls._division_tree

        while l:
            record = cls._traverse(code, l)
            if not record:
                return []

            if record[0] == code:
                return [(i[0], i[1]) for i in record[2]]

            l = record[2]
        return []

    @classmethod
    def is_subdivision_of(cls, code1, code2):
        code1, code2 = unicode_type(code1), unicode_type(code2)
        return code1 in [key for key, _ in cls.traverse(code2)]

    @classmethod
    def top_divisions(cls):
        return [(i[0], i[1]) for i in cls._division_tree]

    @classmethod
    def get_level(cls, code):
        code = unicode_type(code)
        if code.endswith(u'000000000000'):
            return DivisionLevel.country
        elif code.endswith(u'0000000000'):
            return DivisionLevel.province
        elif code.endswith(u'00000000'):
            return DivisionLevel.prefecture
        elif code.endswith(u'000000'):
            return DivisionLevel.county
        else:
            return DivisionLevel.township

    @classmethod
    def jd_4level_code(cls, code):
        l = cls._jd_division_mappings.get(code)
        result = []
        for i in l:
            v = (i, cls._jd_division[i]) if int(i) else None
            result.append(v)
        return result

    @classmethod
    def is_placeholder(cls, code):
        '''省直辖县级行政区划/自治区直辖县级行政区划。不属于正常地区，占位连接直辖县'''
        if code in ('156419000000000', '156429000000000',
                    '156469000000000', '156659000000000'):
            return True
        return False


class DivisionV1(Division):
    _division_tree = simplejson.loads(resource_string(__name__, 'data/division_v1.json'))
    version = '2015-01-01'


class DivisionV2(Division):
    _division_tree = simplejson.loads(resource_string(__name__, 'data/division_v2.json'))
    version = '2015-06-01'


class DivisionV3(Division):
    _division_tree = simplejson.loads(resource_string(__name__, 'data/division_v3.json'))
    version = '2016-02-01'


DIVISION_MAPPINGS = {'2015-01-01': DivisionV1, '2015-06-01': DivisionV2, '2016-02-01': DivisionV3}
