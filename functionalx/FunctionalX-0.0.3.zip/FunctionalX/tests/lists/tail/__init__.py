from . import test_1
from . import test_2
from . import test_3
from FunctionalX import tests

def runtests():
    print(tests.dashed_line(80))
    test_1.run()
    test_2.run()
    test_3.run()
    print(tests.dashed_line(80))