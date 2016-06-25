from FunctionalX import lists 
from FunctionalX import tests

def run():
    print(tests.dashed_line(80,'-'))
    result   = lists.cartn_append([['a','b'],['c','d']], [1,2], ['A','B'])
    solution = [['a', 'b', 1, 'A'], ['a', 'b', 1, 'B'], ['a', 'b', 2, 'A'], ['a', 'b', 2, 'B'], ['c', 'd', 1, 'A'], ['c', 'd', 1, 'B'], ['c', 'd', 2, 'A'], ['c', 'd', 2, 'B']]
    assert result == solution, "ERROR HINT: Test 1 for lists.cartn_append() failed"
    print("Result = ", result,"\n")
    print("lists.cartn_append(): test 1 passed!")
    print(tests.dashed_line(80,'-'))