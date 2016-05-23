# -*- coding: utf-8 -*-
# This file is part of quark-sphinx-theme.
# Copyright (c) 2016 Felix Krull <f_krull@gmx.de>
# Released under the terms of the BSD license; see LICENSE.

from unittest import TestCase

from .util import ExtraAsserts
from quark_sphinx_theme import _mixin


class MixinA:
    def __init__(self, *args, **kwargs):
        pass

    def func_a(self):
        return 'MixinA:func_a'

    def func_b(self):
        return 'MixinA:func_b'


class MixinB(object):
    test_value = None

    __name_tag__ = 'BTag'

    def __init__(self, value):
        self.test_value = value

    def func_a(self):
        return 'MixinB:func_a'

    def func_c(self):
        return 'MixinB:func_c'

    def func_test_value(self):
        return self.test_value


class MixinNoInit:
    def func_c(self):
        return 'MixinNoInit:func_c'


class BaseClass:
    def __init__(self, *args, **kwargs):
        pass

    def func_a(self):
        return 'BaseClass:func_a'

    def func_b(self):
        return 'BaseClass:func_b'

    def func_c(self):
        return 'BaseClass:func_c'

    def func_d(self):
        return 'BaseClass:func_d'


class BaseClassNameTag:
    __name_tag__ = 'BaseTag'


class MixinNoTag:
    __name_tag__ = ''


class TestMixins(ExtraAsserts, TestCase):
    def test_no_mixins(self):
        cls = _mixin.create_compound_class(BaseClass, [])
        self.assertBases(cls, BaseClass, object)
        self.assertEqual(cls.__name__, 'BaseClass')
        inst = cls()
        self.assertEqual(inst.func_a(), 'BaseClass:func_a')
        self.assertEqual(inst.func_b(), 'BaseClass:func_b')
        self.assertEqual(inst.func_c(), 'BaseClass:func_c')
        self.assertEqual(inst.func_d(), 'BaseClass:func_d')

    def test_one_mixin(self):
        cls = _mixin.create_compound_class(BaseClass, [MixinB])
        self.assertBases(cls, BaseClass, MixinB, object)
        self.assertEqual(cls.__name__, 'BTag_BaseClass')
        inst = cls('test_value')
        self.assertEqual(inst.func_a(), 'MixinB:func_a')
        self.assertEqual(inst.func_b(), 'BaseClass:func_b')
        self.assertEqual(inst.func_c(), 'MixinB:func_c')
        self.assertEqual(inst.func_d(), 'BaseClass:func_d')
        self.assertEqual(inst.func_test_value(), 'test_value')

    def test_two_mixins(self):
        cls = _mixin.create_compound_class(BaseClass, [MixinA, MixinB])
        self.assertBases(cls, BaseClass, MixinA, MixinB, object)
        self.assertEqual(cls.__name__, 'MixinA_BTag_BaseClass')
        inst = cls('test_value')
        self.assertEqual(inst.func_a(), 'MixinA:func_a')
        self.assertEqual(inst.func_b(), 'MixinA:func_b')
        self.assertEqual(inst.func_c(), 'MixinB:func_c')
        self.assertEqual(inst.func_d(), 'BaseClass:func_d')
        self.assertEqual(inst.func_test_value(), 'test_value')

    def test_mixin_no_init(self):
        cls = _mixin.create_compound_class(BaseClass, [MixinNoInit])
        self.assertBases(cls, BaseClass, MixinNoInit, object)
        self.assertEqual(cls.__name__, 'MixinNoInit_BaseClass')
        inst = cls()
        self.assertEqual(inst.func_c(), 'MixinNoInit:func_c')

    def test_base_class_name_tag(self):
        cls = _mixin.create_compound_class(BaseClassNameTag, [MixinB])
        self.assertBases(cls, BaseClassNameTag, MixinB, object)
        self.assertEqual(cls.__name__, 'BTag_BaseTag')

    def test_mixin_no_tag(self):
        cls = _mixin.create_compound_class(BaseClass, [MixinA, MixinNoTag])
        self.assertBases(cls, BaseClass, MixinA, MixinNoTag, object)
        self.assertEqual(cls.__name__, 'MixinA_BaseClass')

    def test_explicit_name(self):
        cls = _mixin.create_compound_class(BaseClass, [], 'ExplicitName')
        self.assertEqual(cls.__name__, 'ExplicitName')
