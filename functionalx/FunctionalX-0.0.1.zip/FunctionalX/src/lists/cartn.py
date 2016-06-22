"""
Cartesian product of n lists.

Usage: cartn(list1, list2, ...)
Author: Yuhang(Steven) Wang
Date: 06/21/2016
Copyright: MIT license
"""
def cartn(*all_lists):
    def aux(base_list, lists):
        if len(lists) == 0:
            return base_list 
        elif len(lists) == 1:
            return cart2(base_list, lists[0])
        else:
            return aux(cart_append(base_list, lists[0]), lists[1:])
    if len(all_lists) == 0:
        return []
    elif len(all_lists) == 1:
        return all_lists[0]
    else:
        return aux(all_lists[0], all_lists[1:])

if __name__ == "__main__":
    from cart2 import cart2
    from cart_append import cart_append
    print(cartn(['a','b'], [1,2], ['A','B']))
