from FunctionalX import lists 
from FunctionalX import tests

def run():
    print(tests.dashed_line(80,'-'))
    result   = lists.tail([0,1])
    solution =  [1]
    assert result == solution, "ERROR HINT: Test 3 for lists.tail() failed"
    print("Result = ", result,"\n")
    print("lists.tail(): test 3 passed!")
    print(tests.dashed_line(80,'-'))