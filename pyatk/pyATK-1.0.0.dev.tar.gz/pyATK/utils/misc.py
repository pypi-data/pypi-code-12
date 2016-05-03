# -*- coding: utf-8 -*-


def if_else(condition, value_for_true, value_for_false):
    if (condition) is True:
        return value_for_true
    return value_for_false


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
