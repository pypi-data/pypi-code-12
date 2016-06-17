from __future__ import division

from nose.tools import assert_equal
import types
import os
import sys

from mpiutils import dispatcher

__author__ = 'Ben Kaehler'
__copyright__ = 'Copyright 2016, Ben Kaehler'
__credits__ = ['Ben Kaehler']
__license__ = 'GPL'
__maintainer__ = 'Ben Kaehler'
__email__ = 'benjamin.kaehler@anu.edu.au'
__status__ = 'Production'
__version__ = '0.0.12-dev'

def test_farm():
    size = dispatcher.size()

    def func(dummy):
        return dummy, dispatcher.rank()

    def test_n(n):
        array = range(n)
        result = dispatcher.farm(func, array)
        if result:
            result = list(result)
            if result:
                array, ranks = zip(*result)
                assert_equal(len(array), n)
                assert_equal(set(array), set(range(n)))
                proper_ranks = set(range(min(size-1, 1), min(n+1, size)))
                assert_equal(set(ranks), proper_ranks)

    for n in [size//2, size-1, size, size*2]:
        test_n(n)

def test_farm_gav():
    size = dispatcher.size()

    def func(d1, d2):
        return d1, d2, dispatcher.rank()

    def test_n(n):
        array = range(n)
        result = dispatcher.farm(func, array, array)
        if result:
            result = list(result)
            if result:
                array, array1, ranks = zip(*result)
                assert_equal(array, array1)
                assert_equal(len(array), n)
                assert_equal(set(array), set(range(n)))
                proper_ranks = set(range(min(size-1, 1), min(n+1, size)))
                assert_equal(set(ranks), proper_ranks)

    for n in [size//2, size-1, size, size*2]:
        test_n(n)

def test_map():
    size = dispatcher.size()

    def func(dummy):
        return dummy, dispatcher.rank()

    def test_n(n):
        array = range(n)
        result = dispatcher.map(func, array)
        if result:
            result = list(result)
            if result:
                output, ranks = zip(*result)
                assert_equal(list(output), array)
                proper_ranks = set(range(min(size-1, 1), min(n+1, size)))
                assert_equal(set(ranks), proper_ranks)
    
    for n in [size//2, size-1, size, size*2]:
        test_n(n)

def test_map_gav():
    size = dispatcher.size()

    def func(d1, d2):
        return d1, d2, dispatcher.rank()

    def test_n(n):
        array = range(n)
        result = dispatcher.map(func, array, array)
        if result:
            result = list(result)
            if result:
                output, output1, ranks = zip(*result)
                assert_equal(output, output1)
                assert_equal(list(output), array)
                proper_ranks = set(range(min(size-1, 1), min(n+1, size)))
                assert_equal(set(ranks), proper_ranks)
    
    for n in [size//2, size-1, size, size*2]:
        test_n(n)

def test_imap():
    size = dispatcher.size()

    def func(dummy):
        return dummy, dispatcher.rank()

    def test_n(n):
        array = range(n)
        result = dispatcher.imap(func, array)
        if size != 1:
            assert_equal(type(result), types.GeneratorType)
        result = list(result)
        if result:
            output, ranks = zip(*result)
            assert_equal(list(output), array)
            proper_ranks = set(range(min(size-1, 1), min(n+1, size)))
            assert_equal(set(ranks), proper_ranks)

    for n in [size//2, size-1, size, size*2]:
        test_n(n)


def main():
    test_farm()
    test_map()
    test_imap()

if __name__ == '__main__':
    sys.exit(main())
