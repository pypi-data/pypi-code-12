def cart2(list1: list, list2: list) -> list:
    """Cartesian product of two lists.

    :param list list1: input list 1
    :param list list2: input list 2

    :return: a new list contains all Cartesian products of
        the two lists.
    :rtype: list
    
    >>> cart2(['a','b'], [1,2])
    [['a',1],['a',2],['b',1], ['b',2]]
    """
    def aux(list1: list, list2: list, accum: list) -> list:
        if len(list1) == 0 or len(list2) == 0: # base case
            return accum
        elif len(list1) == 1: # start to traverse list2
            return aux(list1, list2[1:], accum + [[list1[0], list2[0]]])
        else:
            return aux(list1[1:], list2, aux(list1[0:1], list2, accum))
    return aux(list1, list2, [])
