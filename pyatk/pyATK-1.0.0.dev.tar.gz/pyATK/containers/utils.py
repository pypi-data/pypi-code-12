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
        >>> unique([1, 1, 1, 2, 2, 3, 3, 4, 4, 4, 4, 4, 4, 5, 6, 7, 7, 7, 7, 7, 8, 9])
        [1, 2, 3, 4, 5, 6, 7, 8, 9]
        >>> unique((1, 1, 1, 2, 2, 3, 3, 4, 4, 4, 4, 4, 4, 5, 6, 7, 7, 7, 7, 7, 8, 9))
        [1, 2, 3, 4, 5, 6, 7, 8, 9]
        >>> unique(['a', 'z', 'a', 'b', 'a', 'z', 'b'])
        ['a', 'z', 'b']
    """
    return list(set(array))


def same_elements(left, right):
    """
        >>> same_elements([1, 2, 3], [3, 2, 1])
        True
        >>> same_elements([1, 2, 3], [1, 2, 3, 4])
        False
    """
    s1 = set(left)
    s2 = set(right)
    if s1 == s2:
        return True
    return False


def without(lst, element):
    new_lst = []
    for item in lst:
        if item != element:
            new_lst.append(item)
    return new_lst


def union():
    pass


def intersect():
    pass


def difference():
    pass


def index_of(element, lst):
    index = -1
    for item in lst:
        index += 1
        if item == element:
            return index
    return -1


def last_index_of(element, lst):
    index = -1
    while index < len(lst):
        index += 1
        if element == lst[len(lst) - index]:
            return len(lst) - index
    return -1


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
