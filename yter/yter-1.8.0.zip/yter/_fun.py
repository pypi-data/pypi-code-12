"""Functions for getting data from iterators for yter"""

import sys
import bisect
import itertools
import collections


if sys.version_info[0] < 3:
    _stringTypes = (basestring,)
else:
    _stringTypes = (str, bytes)


def yany(y, key=None, empty=False):
    """Extended version of the builtin any, test if any values are true.

    Unlike the builtin `any` method, this will return the last value iterated
    before ending. This will short circuit or exit early when a correct answer
    is found.

    A simple explanation is that this will be the first true value or the
    final false value of the interator. This is the same as calling the
    logical or operator on all the iterated values.

    The `key` is an optional function that will be called on each value in
    iterator. The return of that function will be used to test if the value is
    true or false.

    If the  iterator is empty this will return the empty argument. This
    defaults to False, the same as the built in `any`.

    """
    val = empty
    if key:
        for val in y:
            if key(val):
                return val
    else:
        for val in y:
            if val:
                return val
    return val


def yall(y, key=None, empty=True):
    """Extended version of the builtin all, test if all values are true.

    Unlike the builtin `all` method, this will return the last value iterated
    before ending. This will short circuit or exit early when a correct answer
    is found.

    A simple explanation is that this will be the final true value
    or the first false value of the interator. This is the same as calling the
    logical and operator on all the iterated values.

    The `key` is an optional function that will be called on each value in
    iterator. The return of that function will be used to test if the value is
    true or false.

    If the iterable is empty this will return the empty argument. This
    defaults to True, the same as the built in `all`.

    """
    val = empty
    if key:
        for val in y:
            if not key(val):
                return val
    else:
        for val in y:
            if not val:
                return val
    return val


def first(y, empty=None):
    """Get the final value from an iterator.

    This will get the first value from an iterable object. This is an
    improvement over the builtin `next` because it works on iterable
    objects, not just an iterator. If given an iterator it will be
    advanced by a single value.

    If the iterable contains no values then the `empty` argument is returned.

    """
    head = list(itertools.islice(y, 1))
    if head:
        return head[0]
    return empty


def last(y, empty=None):
    """Get the final value from an iterator.

    This will get the final value from an iterable object. If the iterable
    object can be `reversed` then that will be used to collect only the
    first value.

    If the iterable contains no values then the `empty` argument is returned.

    """
    try:
        ry = reversed(y)
        return next(ry, empty)
    except TypeError:
        val = empty
        for val in y:
            pass
        return val


def head(y, count):
    """Get the first values from an iterator.

    This will be a list of values no larger than `count`. This will
    always advance the iterable object by the given count.
    """
    return list(itertools.islice(y, count))


def tail(y, count):
    """Get the last values from an iterator.

    This will be a list of values no larger than `count`. If the iterable
    object can be `reversed` then that will be used. Otherwise this will
    always finish the iterable object.

    """
    try:
        ry = reversed(y)
    except TypeError:
        return list(collections.deque(y,  maxlen=count))
    else:
        return list(itertools.islice(ry, count))[::-1]


def finish(y):
    """Complete an iterator and get number of values.

    Get all the values from an iterator and return the number of values
    it contained. An empty iterable will return 0.

    """
    span = l = 4096
    count = 0
    while l == span:
        l = len(list(itertools.islice(y, span)))
        count += l
    return count


def minmax(y, key=None, empty=None):
    """Find the minimum and maximum values from an iterable.

    This will always return a tuple of two values. If the iterable contains
    no values it the tuple will contain two values of the `empty` argument.

    The minimum and maximum preserve order. So the first value that compares
    equal will be considered the minimum and the last equal value is
    considered the maximum. If you sorted the iterable, this is the same as
    the first and last values from that list.

    The `key` is an optional function that will be called on each value in
    iterator. The return of that function will be used to sort the values
    from the iterator.

    """
    y = iter(y)
    try:
        minVal = maxVal = next(y)
    except StopIteration:
        return (empty, empty)

    if key:
        minKey = maxKey = key(minVal)
    else:
        minKey = maxKey = minVal

    for curVal in y:
        if key:
            curKey = key(curVal)
        else:
            curKey = curVal

        if curKey < minKey:
            minVal = curVal
            minKey = curKey
        elif curKey >= maxKey:
            maxVal = curVal
            maxKey = curKey
    return (minVal, maxVal)


def minmedmax(y, key=None, empty=None):
    """Find the minimum, median, and maximum values from an iterable.

    This will always return a tuple of three values. If the iterable contains
    no values it the tuple will contain three values of the `empty` argument.

    The minimum and maximum preserve order. So the first value that compares
    equal will be considered the minimum and the last equal value is
    considered the maximum. If you sorted the iterable, this is the same as
    the first and last values from that list.

    Computing the median requires storing half of the iterated values in
    memory. This only keeps the minimum required data, but be aware of
    this overhead when dealing with large iterators.

    The `key` is an optional function that will be called on each value in
    iterator. The return of that function will be used to sort the values
    from the iterator.

    """
    y = iter(y)
    try:
        minVal = maxVal = next(y)
    except StopIteration:
        return (empty, empty, empty)

    if key:
        minKey = maxKey = key(minVal)
    else:
        minKey = maxKey = minVal

    count = 1
    medianVals = [(minKey, minVal)]

    for curVal in y:
        if key:
            curKey = key(curVal)
        else:
            curKey = curVal

        if curKey < minKey:
            minVal = curVal
            minKey = curKey
        elif curKey >= maxKey:
            maxVal = curVal
            maxKey = curKey

        medVal = (curKey, curVal)
        bisect.insort_right(medianVals, medVal)
        count += 1
        if count % 2:
            medianVals.pop()

    medVal = medianVals[-1][1]
    return (minVal, medVal, maxVal)


def isiter(y, ignore=_stringTypes):
    """Test if an object is iterable, but not a string type.

    Test if an object is an iterator or is iterable itself. By default this
    does not return True for string objects.

    The `ignore` argument defaults to a list of string types that are not
    considered iterable. This can be used to also exclude things like
    dictionaries or named tuples.

    """
    if ignore and isinstance(y, ignore):
        return False
    try:
        iter(y)
        return True
    except TypeError:
        return False


def contain(y):
    """Copy an iterator into a list if it is not already a sequence.

    If the value is already a container, like a list or tuple, then return
    the original value. Otherwise the value must be an iterator and it will
    be copied into a sequence.

    """
    if iter(y) is not y:
        return y
    return list(y)


def repeat(y):
    """Return an object that can be iterated multiple times.

    If the value is already a container that can be iterated, that
    that will be returned with no changes. Otherwise this will
    wrap the results in an iterator that copies its values for
    repeated use.

    This allows efficient use of containers when no copy is needed
    to iterate the data multiple times.

    """
    yiter = iter(y)
    if yiter is not y:
        # Object does not need a separate iterator
        return y
    return _Repeat(y)


class _Repeat(object):
    """Allows repeating an iterator any number of times"""
    def __init__(self, it):
        self.__tee1, self.__tee2 = itertools.tee(it)
    def __iter__(self):
        return self.__tee2.__copy__()
