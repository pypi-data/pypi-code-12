import functools
import pydash.arrays as arrays
import itertools


def count(gen):
    return functools.reduce(lambda x,y: x + 1, gen, 0)


def flatten(gen):
    for arr in gen:
        for elem in arrays.flatten(arr, is_deep=True):
            yield elem


def split(gen, n=1):
    """
    Yield successive n-sized chunks from gen.
    Sample usage:
        a = (_ for _ in range(28):
        for chunked in tdash.split(a, n=10):
            print list(chunked)
    Expected output:
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
        [20, 21, 22, 23, 24, 25, 26, 27]

    :param gen
    :param n
    """
    it = iter(gen)
    for first in it:
        yield itertools.chain([first], itertools.islice(it, n - 1))
