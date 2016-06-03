# encoding: utf-8

from zope.component.testlayer import ZCMLFileLayer
from affinitic.caching import memoize

import affinitic.caching
import unittest2
import random


class MemoizeTestClass(object):
    def __init__(self):
        self.calculationCount = 0

    @memoize.cache_for_instances
    def sum(self, a, b):
        self.calculationCount += 1
        return a+b

    @memoize.cache_for_instances
    def list(self, a, b, **kwargs):
        return kwargs


@memoize.cache_for_functions
def memoize_test_function(a, b):
    return random.random()


@memoize.cache_for_functions
def memoize_test_function_list(a, b, **kwargs):
    return kwargs


zcml_file_layer = ZCMLFileLayer(
    affinitic.caching,
    'testing.zcml')


class TestMemoize(unittest2.TestCase):
    layer = zcml_file_layer

    def test_cache_for_instances(self):
        memoize_test = MemoizeTestClass()
        self.assertEqual(3, memoize_test.sum(1, 2))
        self.assertEqual(1, memoize_test.calculationCount)
        self.assertEqual(3, memoize_test.sum(1, 2))
        self.assertEqual(1, memoize_test.calculationCount)
        memoize.clear_cache('affinitic.caching.tests.test_memoize.sum',
                            args=(1, 2))
        self.assertEqual(3, memoize_test.sum(1, 2))
        self.assertEqual(2, memoize_test.calculationCount)

    def test_cache_for_functions(self):
        memoize_test = memoize_test_function
        random_result = memoize_test(1, 2)
        self.assertEqual(random_result, memoize_test(1, 2))
        self.assertNotEqual(random_result, memoize_test(3, 4))
        self.assertEqual(random_result, memoize_test(1, 2))
        memoize.clear_cache('affinitic.caching.tests.test_memoize.memoize_test_function',
                            args=(1, 2))
        self.assertNotEqual(random_result, memoize_test(1, 2))

    def test_functions_list_in_kwargs(self):
        memoize_test = memoize_test_function_list
        list_kwargs = [1, 2, 3]
        result = memoize_test(1, 2, l=list_kwargs)
        self.assertEqual(result, memoize_test(1, 2, l=list_kwargs))
        self.assertEqual(list_kwargs, memoize_test(1, 2, l=list_kwargs)['l'])
        self.assertNotEqual(result, memoize_test(1, 2, l=[1, 2]))

    def test_instances_list_in_kwargs(self):
        memoize_test = MemoizeTestClass()
        memoize_test = memoize_test.list
        list_kwargs = [1, 2, 3]
        result = memoize_test(1, 2, l=list_kwargs)
        self.assertEqual(result, memoize_test(1, 2, l=list_kwargs))
        self.assertEqual(list_kwargs, memoize_test(1, 2, l=list_kwargs)['l'])
        self.assertNotEqual(result, memoize_test(1, 2, l=[1, 2]))
