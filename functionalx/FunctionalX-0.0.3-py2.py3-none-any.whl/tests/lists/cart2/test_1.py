from FunctionalX import lists 
from FunctionalX import tests

def run():
    print(tests.dashed_line(80,'-'))
    result   = lists.cart2(['a','b'], [1,2])
    solution = [['a', 1], ['a', 2], ['b', 1], ['b', 2]]
    assert result == solution, "ERROR HINT: Test 1 for lists.cart2() failed"
    print("Result = ", result,"\n")
    print("lists.cart2(): test 1 passed!")
    print(tests.dashed_line(80,'-'))