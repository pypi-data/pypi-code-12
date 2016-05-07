import os, sys, inspect

# add parent path aka minitest to sys.path, so I can import the files
# realpath() will make your script run, even if you symlink it :)
current_file_path = os.path.split(inspect.getfile( inspect.currentframe() ))[0]
parent_file_path = os.path.realpath(os.path.abspath(os.path.join(current_file_path, '..')))
if parent_file_path not in sys.path:
    sys.path.insert(0, parent_file_path)

from minitest.with_test import *
import minitest.inject_methods

if __name__ == '__main__':
    with test("some"):
        (1).must_equal(1)
        (1).must_equal(2)
        # raise "some"
        pass