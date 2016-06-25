from . import test_1
from FunctionalX import tests

def runtests():
    print(tests.dashed_line(80))
    test_1.run()
    print(tests.dashed_line(80))