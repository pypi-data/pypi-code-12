"""
Cartesian product of two lists.
Usage: cart2(['a','b'], [1,2]) will return [['a',1],['a',2],['b',1], ['b',2]]
Author: Yuhang(Steven) Wang
Date: 06/21/2016
Copyright: MIT license
"""
def cart2(list1, list2):
    def aux(list1, list2, accum):
        if len(list1) == 0 or len(list2) == 0: # base case
            return accum 
        elif len(list1) == 1: # start to traverse list2 
            return aux(list1, list2[1:], accum + [[list1[0], list2[0]]])
        else:
            return aux(list1[1:], list2, aux(list1[0:1], list2, accum))
    return aux(list1, list2,[])

if __name__ == "__main__":
    print(cart2(['a','b'], [1,2]))
