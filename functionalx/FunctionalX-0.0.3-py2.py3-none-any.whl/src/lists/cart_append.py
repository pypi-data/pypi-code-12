"""
Append an element from the second list to the each element from the first list
therefore increase the number of elements in each item in the first list.

Usage: cart_append([[1,2]], ['a','b']) # => [[1,2,'a'], [1,2,'b']]
Author: Yuhang(Steven) Wang
Date: 06/21/2016
"""
def cart_append(list1, list2):
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

if __name__ == "__main__":
    results = cart_append([[1,2],[3,4]], ['A','B'])
    assert(results == [[1, 2, 'A'], [1, 2, 'B'], [3, 4, 'A'], [3, 4, 'B']])
    print(results)