"""A collection of miscellaneous functions to operate on iterables

The pairwise function is different from the recipe version in that it is an
explicit generator that walks the iterable in order to avoid tee.

The partition function is different from the recipe version in that it returns
lists instead of generators as tee would have also generated the overhead and
the predicate would have run twice for each element.

The powerset function is different from the recipe version in that it provides
a reverse argument to allow iteration by size ascendingly and descendingly.
"""
import collections
from itertools import islice, chain, combinations


__all__ = ['chunk', 'divide', 'divide_sizes', 'multi_map', 'pairwise',
           'partition', 'powerset', 'split']


def pairwise(iterable):
    """Pair each element with its neighbors.

    Arguments
    ---------
    iterable : iterable

    Returns
    -------
    The generator produces a tuple containing a pairing of each element with
    its neighbor.
    """
    iterable = iter(iterable)
    left = next(iterable)
    for right in iterable:
        yield left, right
        left = right


def partition(pred, iterable):
    """Partition an iterable.

    Arguments
    ---------
    pred     : function
               A function that takes an element of the iterable and returns
               a boolen indicating to which partition it belongs
    iterable : iterable

    Returns
    -------
    A two-tuple of lists with the first list containing the elements on which
    the predicate indicated False and the second list containing the elements
    on which the predicate indicated True.

    Note that, unlike the recipe which returns generators, this version
    returns lists.
    """
    pos, neg = [], []
    pos_append, neg_append = pos.append, neg.append
    for elem in iterable:
        if pred(elem):
            pos_append(elem)
        else:
            neg_append(elem)
    return neg, pos


def powerset(iterable, *, reverse=False):
    """Return the powerset.

    Arguments
    ---------
    iterable : iterable
    reverse  : boolean
               Indicates whether the powerset should be returned descending by
               size

    Returns
    -------
    A generator producing each element of the powerset.
    """
    lst = list(iterable)
    if reverse:
        rng = range(len(lst), -1, -1)
    else:
        rng = range(len(lst) + 1)
    return chain.from_iterable(combinations(lst, r) for r in rng)


def multi_map(key, iterable, *, default_dict=False):
    """Collect data into a multi-map.

    Arguments
    ----------
    key          : function
                   A function that accepts an element retrieved from the
                   iterable and returns the key to be used in the multi-map
    iterable     : iterable
    default_dict : boolean
                   Indicates whether or not the returned multi-map is an
                   instance of defaultdict(list)

    Returns
    -------
    A dictionary of lists where the dictionary is either an instance of dict()
    or defaultdict(list) based on the *default_dict* boolean and each list
    contains the elements that are associated with the key in the order in
    which they occur in the iterable.
    """
    result = collections.defaultdict(list)
    for rec in iterable:
        result[key(rec)].append(rec)
    return result if default_dict else dict(result)


def split(pred, iterable, *, trailing=True):
    """Split the iterable.

    Arguments
    ----------
    pred     : function
               A function that accepts an element retrieved from the iterable
               and returns a boolean indicating if it is the element on which
               to split
    iterable : iterable
    trailing : boolean
               Indicates whether the split should occur on the leading edge
               of the match on the split or on the trailing edge of the match
               on the split

    Returns
    -------
    The generator produces a list for each split.

    If *trailing* is True then the element that was identified by the predicate
    will be returned at the end of each split.
    If *trailing* is False then the element that was identified by the
    predicate will be returned at the beginning of the following split.

    No guarantee is made regarding the state of the iterable during operation.
    """
    result = []
    result_append = result.append
    if trailing:
        for elem in iterable:
            result_append(elem)
            if pred(elem):
                yield result
                result = []
                result_append = result.append
    else:
        for elem in iterable:
            if pred(elem):
                if result:
                    yield result
                result = []
                result_append = result.append
            result_append(elem)
    if result:
        yield result


def chunk(iterable, length):
    """Collect data into chunks.

    Arguments
    ---------
    iterable : iterable
    length   : integer
               Maximum size of each chunk to return

    Returns
    -------
    The generator produces a tuple of elements whose size is at least one but
    no more than *length*.

    If the number of elements in the iterable is not a multiple of *length*
    then the final tuple will be less than *length*.

    This function is meant to be a variant of the recipe's function grouper()
    that does not pad the last tuple with a fill-value if the number elements
    in the iterable is not a multiple of the specified length.
    """
    if length < 0:
        return ()
    iterable = iter(iterable)
    result = tuple(islice(iterable, length))
    while result:
        yield result
        result = tuple(islice(iterable, length))


def divide(iterable, n):                # pylint: disable=invalid-name
    """Evenly divide elements.

    Arguments
    ---------
    iterable : iterable
    n        : integer
               The number of buckets in which to divide the elements

    Returns
    -------
    The generator produces *n* tuples, each containing a number of elements
    where the number is calculated to be evenly distributed across all of the
    returned tuples.

    The number of tuples returned is always *n* and, thus, may return an empty
    tuple if there is not enough data to distribute.

    In order to determine the number of elements to put in each tuple, the
    iterable is converted into a list. Consider using divide_sizes() and
    manually slicing the iterator if this is not desirable.
    """
    if n <= 0:
        return []
    data = list(iterable)
    base, rem = divmod(len(data), n)
    iterable = iter(data)
    for i in range(n):
        yield tuple(islice(iterable, base + 1 if i < rem else base))


def divide_sizes(count, n):             # pylint: disable=invalid-name
    """Evenly divide a count.

    Arguments
    ---------
    count : integer
            The number to be evenly divided
    n     : integer
            The number of buckets in which to divide the number

    Returns
    -------
    A list of integers indicating what size each bucket should be for an even
    distribution of *count*.

    The number of integers returned is always *n* and, thus, may be 0.

    Useful for calculating slices for generators that might be too large to
    convert into a list as happens in divide().
    """
    if n <= 0:
        return []
    if count < 0:
        return [0] * n
    base, rem = divmod(count, n)
    return [base + 1 if i < rem else base for i in range(n)]
