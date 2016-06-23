from FunctionalX import lists 
from FunctionalX import tests

def run():
    print(tests.dashed_line(80,'-'))
    result   = lists.dict2list({
        "a": {
            1: "A",
            2: "B"
        },
        "b": {
            3: "C",
            4: "D"
        }
        })
    solution =  [['a', 1, 'A'], ['a', 2, 'B'], ['b', 3, 'C'], ['b', 4, 'D']]
    print("Result = ", result,"\n")
    # note the result may not be the same for each run 
    # due to the lack of order in dict.
    assert sorted(result) == solution, "ERROR HINT: Test 1 for lists.dict2list() failed"
    print("lists.dict2list(): test 1 passed!")
    print(tests.dashed_line(80,'-'))