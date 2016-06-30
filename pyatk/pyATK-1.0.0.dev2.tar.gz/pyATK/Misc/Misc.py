# -*- coding: utf-8 -*-


def if_else(condition, value_for_true, value_for_false):
    """
    >>> if_else(True, 1, 0)
    1
    >>> if_else(False, 1, 0)
    0
    >>> if_else(5 > 3 and 4 > 2, True, False)
    True
    """
    if (condition) is True:
        return value_for_true
    return value_for_false

