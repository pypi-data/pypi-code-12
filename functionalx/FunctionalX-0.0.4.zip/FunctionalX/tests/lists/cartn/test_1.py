from FunctionalX import lists 
from FunctionalX import tests

def run():
    print(tests.dashed_line(80,'-'))
    result   = lists.cartn(['a','b'], [1,2], ['A','B'])
    solution = [['a', 1, 'A'], ['a', 1, 'B'], ['a', 2, 'A'], ['a', 2, 'B'], ['b', 1, 'A'], ['b', 1, 'B'], ['b', 2, 'A'], ['b', 2, 'B']]
    assert result == solution, "ERROR HINT: Test 1 for lists.cartn() failed"
    print("Result = ", result,"\n")
    print("lists.cartn(): test 1 passed!")
    print(tests.dashed_line(80,'-'))