# Copyright (C) 2016 Barry Warsaw
#
# This project is licensed under the terms of the Apache 2.0 License.  See
# LICENSE.txt for details.

import os
import sys
import builtins
import unittest

from _public import public as c_public
from contextlib import ExitStack, contextmanager
from importlib import import_module
from public import install as c_install, py_install
from public.public import public as py_public
from tempfile import TemporaryDirectory


@contextmanager
def syspath(directory):
    try:
        sys.path.insert(0, directory)
        yield
    finally:
        assert sys.path[0] == directory
        del sys.path[0]


@contextmanager
def sysmodules():
    modules = sys.modules.copy()
    try:
        yield
    finally:
        sys.modules = modules


class TestPublic(unittest.TestCase):
    import_line = 'from public import public'

    def setUp(self):
        self.resources = ExitStack()
        self.tmpdir = self.resources.enter_context(TemporaryDirectory())
        self.resources.enter_context(syspath(self.tmpdir))
        self.resources.enter_context(sysmodules())
        self.addCleanup(self.resources.close)

    def test_atpublic_function(self):
        modpath = os.path.join(self.tmpdir, 'function.py')
        with open(modpath, 'w', encoding='utf-8') as fp:
            print("""\
{}

@public
def a_function():
    pass
""".format(self.import_line), file=fp)
        module = import_module('function')
        self.assertEqual(module.__all__, ['a_function'])

    def test_atpublic_function_runnable(self):
        modpath = os.path.join(self.tmpdir, 'function.py')
        with open(modpath, 'w', encoding='utf-8') as fp:
            print("""\
{}

@public
def a_function():
    return 1
""".format(self.import_line), file=fp)
        module = import_module('function')
        self.assertEqual(module.a_function(), 1)

    def test_atpublic_class(self):
        modpath = os.path.join(self.tmpdir, 'classy.py')
        with open(modpath, 'w', encoding='utf-8') as fp:
            print("""\
{}

@public
class AClass:
    pass
""".format(self.import_line), file=fp)
        module = import_module('classy')
        self.assertEqual(module.__all__, ['AClass'])

    def test_atpublic_class_runnable(self):
        modpath = os.path.join(self.tmpdir, 'classy.py')
        with open(modpath, 'w', encoding='utf-8') as fp:
            print("""\
{}

@public
class AClass:
    pass
""".format(self.import_line), file=fp)
        module = import_module('classy')
        self.assertIsInstance(module.AClass(), module.AClass)

    def test_atpublic_two_things(self):
        modpath = os.path.join(self.tmpdir, 'twothings.py')
        with open(modpath, 'w', encoding='utf-8') as fp:
            print("""\
{}

@public
def foo():
    pass

@public
class AClass:
    pass
""".format(self.import_line), file=fp)
        module = import_module('twothings')
        self.assertEqual(module.__all__, ['foo', 'AClass'])

    def test_atpublic_append_to_all(self):
        modpath = os.path.join(self.tmpdir, 'append.py')
        with open(modpath, 'w', encoding='utf-8') as fp:
            print("""\
__all__ = ['a', 'b']

a = 1
b = 2

{}

@public
def foo():
    pass

@public
class AClass:
    pass
""".format(self.import_line), file=fp)
        module = import_module('append')
        self.assertEqual(module.__all__, ['a', 'b', 'foo', 'AClass'])

    def test_atpublic_keywords(self):
        modpath = os.path.join(self.tmpdir, 'keywords.py')
        with open(modpath, 'w', encoding='utf-8') as fp:
            print("""\
{}

public(a=1, b=2)
""".format(self.import_line), file=fp)
        module = import_module('keywords')
        self.assertEqual(sorted(module.__all__), ['a', 'b'])

    def test_atpublic_keywords_multicall(self):
        modpath = os.path.join(self.tmpdir, 'keywords.py')
        with open(modpath, 'w', encoding='utf-8') as fp:
            print("""\
{}

public(b=1)
public(a=2)
""".format(self.import_line), file=fp)
        module = import_module('keywords')
        self.assertEqual(module.__all__, ['b', 'a'])

    def test_atpublic_keywords_global_bindings(self):
        modpath = os.path.join(self.tmpdir, 'keywords.py')
        with open(modpath, 'w', encoding='utf-8') as fp:
            print("""\
{}

public(a=1, b=2)
""".format(self.import_line), file=fp)
        module = import_module('keywords')
        self.assertEqual(module.a, 1)
        self.assertEqual(module.b, 2)

    def test_atpublic_mixnmatch(self):
        modpath = os.path.join(self.tmpdir, 'mixnmatch.py')
        with open(modpath, 'w', encoding='utf-8') as fp:
            print("""\
__all__ = ['a', 'b']

a = 1
b = 2

{}

@public
def foo():
    pass

@public
class AClass:
    pass

public(c=3)
""".format(self.import_line), file=fp)
        module = import_module('mixnmatch')
        self.assertEqual(module.__all__, ['a', 'b', 'foo', 'AClass', 'c'])


class TestPyPublic(TestPublic):
    import_line = 'from public import py_public as public'


class TestInstall(unittest.TestCase):
    def test_install_c_public(self):
        self.assertFalse(hasattr(builtins, 'public'))
        self.addCleanup(delattr, builtins, 'public')
        c_install()
        self.assertTrue(hasattr(builtins, 'public'))
        self.assertIs(builtins.public, c_public)

    def test_install_py_public(self):
        self.assertFalse(hasattr(builtins, 'public'))
        self.addCleanup(delattr, builtins, 'public')
        py_install()
        self.assertTrue(hasattr(builtins, 'public'))
        self.assertIs(builtins.public, py_public)
