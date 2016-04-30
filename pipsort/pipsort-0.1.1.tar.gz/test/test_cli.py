""" Test suite for the cli module.

The script can be executed on its own or incorporated into a larger test suite.
However the tests are run, be aware of which version of the module is actually
being tested. If the library is installed in site-packages, that version takes
precedence over the version in this project directory. Use a virtualenv test
environment or setuptools develop mode to test against the development version.

"""
from subprocess import call
from sys import executable

import pytest
from pipsort.cli import *  # test __all__

def test_main():
    """ Test the main() function.

    """
    # Call with the --help option as a basic sanity check.
    with pytest.raises(SystemExit) as exinfo:
        main(("", "--help"))
    print "help..."*100
    assert 0 == exinfo.value.code
    return


def test_script():
    """ Test command line execution.

    """
    # Call with the --help option as a basic sanity check.
    cmdl = "{:s} -m pipsort.cli --help".format(executable)
    assert 0 == call(cmdl.split())
    return

def test_script_without_search_term():
    cmdl = "{:s} -m pipsort.cli".format(executable)
    assert 0 != call(cmdl.split())
    return

def test_script_with_search_term():
    cmdl = "{:s} -m pipsort.cli".format(executable)

# Make the script executable.

if __name__ == "__main__":
    raise SystemExit(pytest.main(__file__))
