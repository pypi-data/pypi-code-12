# coding: utf-8

from __future__ import unicode_literals, print_function

from ._compat import unicode_type, UnicodeMixin
from .division import DIVISION_MAPPINGS
from .exceptions import InvalidRegionException
from .utils import normalize_name, cached_property


class Region(UnicodeMixin):

    def __init__(self, code, name, version):
        self.id = int(code)
        self.code = unicode_type(code)
        self.name = unicode_type(name)
        self.version = version

    def __hash__(self):
        return hash(self.code)

    def __eq__(self, other):
        if not isinstance(other, Region):
            return False
        return self.code == other.code

    def __repr__(self):
        return 'Region.get(%r)' % self.code

    def __unicode__(self):
        return '<Region %s/%s>' % (self.code, '/'.join([i.name for i in self.stack]))

    @cached_property
    def stack(self):
        division_model = DIVISION_MAPPINGS[self.version]
        return [Region(code, name, self.version) for code, name in division_model.get_stack(self.code) if code]

    @property
    def stack_name(self):
        return ' '.join([i.name for i in self.stack])

    @property
    def level(self):
        division_model = DIVISION_MAPPINGS[self.version]
        return division_model.get_level(self.code)

    @property
    def jd_4level_code(self):
        '''
        [("29", u"青海"), ("2612", u"玉树州"), ("2614", u"称多县"), ("18278", u"称文镇")]
        [("1", u"北京"), ("2803", u"崇文区"), None, None]
        '''
        division_model = DIVISION_MAPPINGS[self.version]
        return division_model.jd_4level_code(self.code)

    def is_placeholder(self):
        division_model = DIVISION_MAPPINGS[self.version]
        return division_model.is_placeholder(self.code)

    def is_in_region(self, other_region):
        return other_region.code in [r.code for r in self.stack]

    def is_in_regions(self, other_regions):
        return bool(set([r.code for r in self.stack]) & set([r.code for r in other_regions]))

    def get_subregions(self):
        division_model = DIVISION_MAPPINGS[self.version]
        return [Region(code, name, self.version) for code, name in division_model.traverse(self.code)]

    def parent(self):
        if len(self.stack) > 1:
            return self.stack[-2]
        return None

    def descendants(self):
        objs = []
        for r in self.children():
            objs.append(r)
            objs.extend(r.descendants)
        return objs

    def ancestors(self):
        return self.stack

    children = get_subregions


def get_region(code):
    code = unicode_type(code)

    for _, division_model in sorted(DIVISION_MAPPINGS.items(), key=lambda x: x[0], reverse=True):
        name = division_model.get_name(code)
        if name:
            return Region(code, name, division_model.version)
    raise InvalidRegionException


def get_region_by_stack_name(stack_name):
    stack_name = unicode_type(stack_name)
    stack_name = normalize_name(stack_name)

    last_code = ''
    for _, division_model in sorted(DIVISION_MAPPINGS.items(), key=lambda x: x[0], reverse=True):
        l = []
        for level, name in enumerate(stack_name.split()):
            if level == 0:
                items = division_model.top_divisions()
            else:
                items = division_model.traverse(last_code)
            l = [(_code, _name) for _code, _name in items if name == _name]
            if not l:
                break

            last_code = l[0][0]

        if l:
            return get_region(last_code)

    raise InvalidRegionException


def get_top_regions():
    latest_division_model = sorted(DIVISION_MAPPINGS.items(), key=lambda x: x[0], reverse=True)[0][1]
    return [Region(code, value, latest_division_model.version) for code, value in latest_division_model.top_divisions()]
