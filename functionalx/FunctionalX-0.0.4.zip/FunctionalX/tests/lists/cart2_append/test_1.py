from FunctionalX import lists 
from FunctionalX import tests

def run():
    print(tests.dashed_line(80,'-'))
    result   = lists.cart2_append(['a','b'], [1,2])
    solution = [['a', 'b', 1], ['a', 'b', 2]]
    assert result == solution, "ERROR HINT: Test 1 for lists.cart2_append() failed"
    print("Result = ", result,"\n")
    print("lists.cart2_append(): test 1 passed!")
    print(tests.dashed_line(80,'-'))