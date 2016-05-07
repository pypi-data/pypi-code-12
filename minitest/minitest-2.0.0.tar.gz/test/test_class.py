import os, sys, inspect
import ctypes

# add parent path aka minitest to sys.path, so I can import the files
# realpath() will make your script run, even if you symlink it :)
current_file_path = os.path.split(inspect.getfile( inspect.currentframe() ))[0]
parent_file_path = os.path.realpath(os.path.abspath(os.path.join(current_file_path, '..')))
if parent_file_path not in sys.path:
    sys.path.insert(0, parent_file_path)

class Person(object):
    pass

def pm(self):
    print "pm"

def get_dict(obj):
    _get_dict = ctypes.pythonapi._PyObject_GetDictPtr
    _get_dict.restype = ctypes.POINTER(ctypes.py_object)
    _get_dict.argtypes = [ctypes.py_object]
    return _get_dict(obj).contents.value

def set_method_to_builtin(clazz, method_func, method_name=None):
    method_name = method_name or method_func.func_code.co_name
    get_dict(clazz)[method_name] = method_func

if __name__ == '__main__':
    from minitest import *

    with test(Person):
        colin = Person()
        set_method_to_builtin(object, pm, 'pm')
        set_method_to_builtin(type, pm, 'pm')
        print colin.__class__.__class__
        print type
        # colin.__class__.p()
        colin.__class__.pm()
        # None.pm()