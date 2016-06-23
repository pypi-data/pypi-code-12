from FunctionalX import lists 
from FunctionalX import tests

def run():
    print(tests.dashed_line(80,'-'))
    result   = lists.tail([0])
    solution =  []
    assert result == solution, "ERROR HINT: Test 2 for lists.tail() failed"
    print("Result = ", result,"\n")
    print("lists.tail(): test 2 passed!")
    print(tests.dashed_line(80,'-'))