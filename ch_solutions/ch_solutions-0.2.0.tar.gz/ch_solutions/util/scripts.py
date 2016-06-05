import os
import sys


def _get_script_name():
    return os.path.basename(sys.argv[0])[:-3]


def get_script_name():
    try:
        if script_name:
            return script_name
    except NameError:
        set_script_name('test_name')
        return


def set_script_name(name=None):
    if name is None:
        name = _get_script_name()
    global script_name
    script_name = name

