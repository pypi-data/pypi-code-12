'''
:py:mod:`a2m.itertools` is a collection of functions and classes
implementing some convenient iteration recipes.

..  todo::
    Write module-level documentation part.

..  testsetup:: *

    from a2m.itertools import *
'''

from __future__ import absolute_import

import itertools
import six


__all__ = ('even', 'odd', 'every_nth', 'flatten')


def flatten(thing, protected_iterables=(), enforce_scalar=None):
    '''
    Takes an iterable of nested iterables and scalars and traverses it into a flat sequence.

    :param thing: a nested iterable of arbitrary depth,

    :param protected_iterables: a list of types which should be treated as scalars unconditionally,

    :param enforce_scalar: a callable that takes single argument
        and defines if its value should be protected from flattenting.
        Provides more flexible way to protect values on instance level.
    :type enforce_scalar: callable or ``None``

    :rtype: generator iterator
    :return: a flat sequence of all elements from source iterable.

    Here are some examples. Flatten everything:

    ..  doctest::

        >>> seq = [(1, 2), [3, (4,), 5, 5.5], 6, [7, 8]]
        >>> list(flatten(seq))
        [1, 2, 3, 4, 5, 5.5, 6, 7, 8]

    Flatten everything but tuples:

    ..  doctest::

        >>> seq = [(1, 2), [3, (4,), 5, 5.5], 6, [7, 8]]
        >>> list(flatten(seq, protected_iterables=(tuple,)))
        [(1, 2), 3, (4,), 5, 5.5, 6, 7, 8]

    Flatten, but protect sequences shorter than 3 elements:

    ..  doctest::

        >>> seq = [(1, 2), [3, (4,), 5, 5.5], 6, [7, 8]]
        >>> protect_short = lambda s: hasattr(s, '__iter__') and len(tuple(s)) < 3
        >>> list(flatten(seq, enforce_scalar=protect_short))
        [(1, 2), 3, (4,), 5, 5.5, 6, [7, 8]]

    **Note:** Strings are always protected. If you wants to flatten a nested iterable
    of strings into single one, follow this example:

    ..  doctest::

        >>> lst = list(flatten(['a', ['sequence', ['of'], 'strings']]))
        >>> lst
        ['a', 'sequence', 'of', 'strings']
        >>> ''.join(lst)
        'asequenceofstrings'

    And if a character-wise iterator is required, this recipe can be used:

    ..  doctest::

        >>> import itertools
        >>> it = itertools.chain(*flatten(['a', ['sequence', ['of'], 'strings']]))
        >>> it
        <itertools.chain object at 0x...>
        >>> list(it)
        ['a', 's', 'e', 'q', 'u', 'e', 'n', 'c', 'e', 'o', 'f', 's', 't', 'r', 'i', 'n', 'g', 's']

    '''
    iterators = []
    it = iter(thing)
    protected_iterables = six.string_types + tuple(protected_iterables)
    while True:
        try:
            thing = next(it)
        except StopIteration:
            try:
                it = iterators.pop()
            except IndexError:
                return
        else:
            try:
                if (
                    isinstance(thing, protected_iterables) or
                    callable(enforce_scalar) and enforce_scalar(thing)
                ):
                    raise ValueError(thing)
                _ = iter(thing)
            except (TypeError, ValueError):
                yield thing
            else:
                iterators.append(it)
                it = _


def every_nth(thing, n, shift=0):
    '''
    Takes an iterable and returns every n-th element from beginning, optionally shifted by ``shift``

    This funcion is just a handy wrapper over :py:func:`itertools.islice`.
    Indexes are 1-based.

    :param thing: an arbitrary iterable
    :param int n: enumerator defining sequence step
    :param int shift: pattern cycling shift (negative values are accepted)

    Example:

    ..  doctest::

        >>> it = every_nth(range(20), 3)
        >>> it
        <itertools.islice object at 0x...>
        >>> list(it)
        [2, 5, 8, 11, 14, 17]

    Another example, with non-zero ``shift``:

    ..  doctest::

        >>> it = every_nth(range(20), 3, 2)
        >>> it
        <itertools.islice object at 0x...>
        >>> list(it)
        [1, 4, 7, 10, 13, 16, 19]

    ..  doctest::

        >>> list(every_nth(range(20), 4, -1))
        [2, 6, 10, 14, 18]

    '''
    if not isinstance(n, int):
        raise TypeError('n: an integer is required')
    if not isinstance(shift, int):
        raise TypeError('shift: an integer is required')

    if n < 1:
        raise ValueError('n: a positive non-zero integer is required')
    elif n == 1:
        it = iter(thing)
    else:
        # decrease the ``shift`` by unit to ensure indexes are 1-based
        it = itertools.islice(thing, (shift - 1) % n, None, n)

    return it


def even(thing):
    '''
    Filter all even elements of a sequence.

    :param thing: an arbitrary iterable
    :rtype: :py:func:`itertools.islice` iterator
    :returns: iterator over all even elements of given sequence

    This function is just a wrapper over :py:func:`itertools.islice`.
    Indexes are 1-based.

    Example:

    ..  doctest::

        >>> it = even('abcdef')
        >>> it
        <itertools.islice object at 0x...>
        >>> list(it)
        ['b', 'd', 'f']

    '''
    return itertools.islice(thing, 1, None, 2)


def odd(thing):
    '''
    Filter all odd elements of a sequence.

    :param thing: an arbitrary iterable
    :rtype: :py:func:`itertools.islice` iterator
    :returns: iterator over all odd elements of given sequence

    This function is just a wrapper over :py:func:`itertools.islice`.
    Indexes are 1-based.

    Example:

    ..  doctest::

        >>> it = odd('abcdef')
        >>> it
        <itertools.islice object at 0x...>
        >>> list(it)
        ['a', 'c', 'e']
    '''
    return itertools.islice(thing, 0, None, 2)


if __name__ == '__main__':
    six.print_(list(flatten(([1, 2], [3, [4], 5, 5.5], 6, [7, 8]))))
