from FunctionalX import lists 
from FunctionalX import tests

def run():
    print(tests.dashed_line(80,'-'))
    result   = lists.tail([])
    solution =  []
    assert result == solution, "ERROR HINT: Test 1 for lists.tail() failed"
    print("Result = ", result,"\n")
    print("lists.tail(): test 1 passed!")
    print(tests.dashed_line(80,'-'))