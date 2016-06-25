from ._cart2_append import cart2_append
from ._cart2 import cart2
from ._tail import tail

def cartn(*all_lists: list) -> list:
    """Cartesian product of n lists.

    :param list all_lists(vararg): variable number of lists
    :return: a new list
    :rtype: list
      
    >>> cartn(['a','b'], [1,2], ['A','B'])
    [['a', 1, 'A'], ['a', 1, 'B'], ['a', 2, 'A'], ['a', 2, 'B'], ['b', 1, 'A'], ['b', 1, 'B'], ['b', 2, 'A'], ['b', 2, 'B']]  
    """
    def aux(base_list: list, lists: list) -> list:
        if len(lists) == 0:
            return base_list 
        else:
            return aux(cart2_append(base_list, lists[0]), tail(lists))
    
    if len(all_lists) == 0:
        return []
    elif len(all_lists) == 1:
        return all_lists
    else:
        return aux(cart2(all_lists[0], all_lists[1]), tail(all_lists[1:]))
