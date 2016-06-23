from FunctionalX import lists 
from FunctionalX import tests

def run():
    print(tests.dashed_line(80,'-'))
    result   = lists.head([1,2])
    solution = 1
    print("Result = ", result,"\n")
    assert result == solution, "ERROR HINT: Test 2 for lists.head() failed"
    print("lists.head(): test 2 passed!")
    print(tests.dashed_line(80,'-'))
