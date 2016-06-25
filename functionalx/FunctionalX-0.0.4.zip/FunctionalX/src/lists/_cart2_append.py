def cart2_append(list1, list2):
    """Append items from list2 to list1 for all possible pairs.

    Append an element from the second list to the each element from the first list
    therefore increase the number of elements in each item in the first list.

    :param list list1: input list 1
    :param list list2: input list 2

    :return: a new list.
    :rtype: list

    >>> cart_append([[1,2]], ['a','b']) 
    [[1,2,'a'], [1,2,'b']]
    """
    def others(list1):
        if len(list1) <= 1:
            return []
        else:
            return list1[1:]

    def aux(list1, list2, accum):
        if len(list1) == 0 or len(list2) == 0:
            return accum 
        elif isinstance(list1[0], list):
            return aux(others(list1), list2, aux(list1[0], list2, accum))
        else:
            return aux(list1, others(list2), accum + [list1 + [list2[0]]])

    return aux(list1, list2, [])
