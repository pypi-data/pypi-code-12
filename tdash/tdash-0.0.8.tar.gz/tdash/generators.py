import functools
import pydash.arrays as arrays

def count(gen):
    return functools.reduce(lambda x,y: x + 1, gen, 0)

def flatten(gen):
    for arr in gen:
        for elem in arrays.flatten(arr, is_deep=True):
            yield elem
