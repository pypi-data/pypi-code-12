from FunctionalX import lists 
from FunctionalX import tests

def run():
    print(tests.dashed_line(80,'-'))
    result   = lists.head([])
    solution = None
    print("Result = ", result,"\n")
    assert result == solution, "ERROR HINT: Test 1 for lists.head() failed"
    print("lists.head(): test 1 passed!")
    print(tests.dashed_line(80,'-'))