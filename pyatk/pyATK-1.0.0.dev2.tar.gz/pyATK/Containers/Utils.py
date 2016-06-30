#!/usr/bin/python3
# -*- coding: utf-8 -*-


def flatten(lst):
    """
    >>> flatten([[[1], 2, [3, 4]], 5, [6], [7, 8, 9]])
    [1, 2, 3, 4, 5, 6, 7, 8, 9]
    """
    l = []
    for item in lst:
        if isinstance(item, list):
            l.extend(flatten(item))
        else:
            l.append(item)

    return l


def unique(array):
    """
        >>> unique([1, 2, 1, 2, 5, 3, 3, 4, 4, 1, 1, 1, 4, 5, 6, 7, 7, 6, 8, 7, 8, 9])
        [1, 2, 3, 4, 5, 6, 7, 8, 9]
        >>> unique((1, 1, 1, 2, 2, 3, 3, 4, 4, 4, 4, 4, 4, 5, 6, 7, 7, 7, 7, 7, 8, 9))
        [1, 2, 3, 4, 5, 6, 7, 8, 9]
        >>> unique(['a', 'z', 'a', 'b', 'a', 'z', 'b'])
        ['a', 'b', 'z']
    """
    return sorted(list(set(array)))


def sameElements(left, right):
    """
        >>> sameElements([1, 2, 3], [3, 2, 1])
        True
        >>> sameElements([1, 2, 3], [1, 2, 3, 4])
        False
    """
    s1 = set(left)
    s2 = set(right)
    if s1 == s2:
        return True
    return False


def without(lst, element):
    """
    >>> without([1, 2, 3, 4, 5], 5)
    [1, 2, 3, 4]
    >>> without([1, 2, 3], 2)
    [1, 3]
    """
    new_lst = []
    for item in lst:
        if item != element:
            new_lst.append(item)
    return new_lst


def indexOf(element, lst):
    """
    >>> indexOf('e', "Hello There")
    1
    >>> indexOf(1, [0, 2, 3])
    -1
    """
    index = -1
    for item in lst:
        index += 1
        if item == element:
            return index
    return -1


def lastIndexOf(element, lst):
    """
    >>> lastIndexOf(1, [1, 2, 3, 1, 5, 6, 1])
    6
    >>> lastIndexOf(10, [1, 2, 3, 1, 5, 6, 1])
    -1
    """
    index = -1
    while index < len(lst):
        index += 1
        if element == lst[len(lst) - index - 1]:
            return len(lst) - index - 1
    return -1

