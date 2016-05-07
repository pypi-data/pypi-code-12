import sys
import ctypes
import inspect
import operator
import traceback
import pprint

if sys.version_info < (3, 0):
    from cStringIO import StringIO
    import new
    import __builtin__ as builtins
    from types import NoneType

    from variables import *
else:
    from io import StringIO
    import builtins
    NoneType = type(None)

    try:
        from .variables import *
        # this for python 3 __main__, ugly!!
    except SystemError:
        from variables import *




__all__ = []

class capture_output(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        sys.stdout = self._stdout

def get_dict(obj):
    _get_dict = ctypes.pythonapi._PyObject_GetDictPtr
    _get_dict.restype = ctypes.POINTER(ctypes.py_object)
    _get_dict.argtypes = [ctypes.py_object]
    return _get_dict(obj).contents.value

def set_method_to_builtin(clazz, method_func, method_name=None):
    if sys.version_info < (3, 0):
        method_name = method_name or method_func.func_code.co_name
    else:
        method_name = method_name or method_func.__code__.co_name

    get_dict(clazz)[method_name] = method_func

def set_method_to_object(method_func, method_name=None):
    set_method_to_builtin(object, method_func, method_name)

def run_compare(actual, expected = True, func = operator.eq,
        failure_msg=None):

    try:            
        if actual == NoneType:
            actual = None
    except ValueError as e:
    # change for python 3
    # except ValueError, e:
        pass
        
    test_case = get_current_test_case()
    test_case.add_assertion()
    if not func(actual, expected):
        frame = inspect.getouterframes(inspect.currentframe())[-1]
        test_case.add_failure(actual = actual, expected = expected, 
            frame = frame, failure_msg = failure_msg)
        get_current_test_method().set_failed()
    return actual

def must_equal(self, other, key=operator.eq, failure_msg=None):
    return run_compare(self, other, key, failure_msg=failure_msg)

def must_equal_with_func(self, other, func, failure_msg=None):
    ''' deprecated, now just use must_equal's key parameter '''
    return run_compare(self, other, func, failure_msg=failure_msg)

def must_true(self, failure_msg=None):
    return run_compare(self, failure_msg=failure_msg)

def must_false(self, failure_msg=None):
    return run_compare(self, expected = False, failure_msg=failure_msg)

def must_raise(self, raised_exception, exception_msg=None, failure_msg=None):
    if hasattr(self, '__call__'):
        try:
            result = self()
            return run_compare(None, raised_exception, failure_msg=failure_msg)
        except Exception as e:
            if type(e) == raised_exception and exception_msg != None:
                return run_compare(str(e), exception_msg, failure_msg=failure_msg)
            else:
                return run_compare(type(e), raised_exception, failure_msg=failure_msg)
    else:
        "It must be a function."

def must_output(self, expected_output, failure_msg=None):
    if hasattr(self, '__call__'):
        with capture_output() as output:
            result = self()
        return run_compare(output, expected_output, failure_msg=failure_msg)
    else:
        "It must be a function."


# def gen_title_from_stack_info(stack_info):
#     ''' it will generate the title from stack info.

#     '''
#     text  = stack_info[-2][-1]
#     index = text.rfind(".")
#     return text[:index]+" :"

def gen_title_from_stack_info(stack_info, func_name):
    ''' it will generate the title from stack info.

    '''
    text  = stack_info[-2][-1]
    index = text.rfind("."+func_name)
    return text[:index]+" :"

def gen_line_info(frame):
    '''
        the parameter 'frame' will like:
        (<frame object at 0x7fb521c7c8e0>,
         '/Users/Colin/work/minitest/minitest/with_test.py',
         233,
         '<module>',
         ['    tself.jc.ppl()\n'],
         0)
    '''
    return 'File "%s", line %d, in %s:' % (frame[1], frame[2], frame[3])

def p(self, title=None, auto_get_title=True):
    self_func_name = 'p'
    result = self
    # if type(result) == NoneType:
    #     result = None
    if title:
        print(title, result)
    else:
        if auto_get_title:
            print(gen_title_from_stack_info(
                traceback.extract_stack(), self_func_name), result)
        else:
            print(result)
    return result

def pp(self, title=None, auto_get_title=True):
    self_func_name = 'pp'
    result = self
    # if type(result) == NoneType:
    #     result = None
    if title:
        print(title)
    else:
        if auto_get_title:
            print(gen_title_from_stack_info(
                traceback.extract_stack(), self_func_name))
    pprint.pprint(result)
    return result

def p_format(self):
    self_func_name = 'p_format'
    title = gen_title_from_stack_info(
        traceback.extract_stack(), self_func_name)
    return "%s %s" % (title, self)

def pp_format(self):
    self_func_name = 'pp_format'
    title = gen_title_from_stack_info(
        traceback.extract_stack(), self_func_name)
    return "%s\n%s" % (title, pprint.pformat(self))

def pl_format(self):
    self_func_name = 'pl_format'
    title = gen_title_from_stack_info(
        traceback.extract_stack(), self_func_name)
    current_frame = inspect.getouterframes(inspect.currentframe())[1]
    return "line info: %s\n%s\n%s" % (gen_line_info(current_frame), title, self)

def ppl_format(self):
    self_func_name = 'ppl_format'
    title = gen_title_from_stack_info(
        traceback.extract_stack(), self_func_name)
    current_frame = inspect.getouterframes(inspect.currentframe())[1]
    return "line info: %s\n%s\n%s" % (gen_line_info(current_frame), title, pprint.pformat(self))

def pl(self, title=None, auto_get_title=True):
    ''' p with line information including file full path and line number.
        Notice, it will print new line firstly, since in some case, 
        there will be other string before file path
        and some editor cannot jump to the location.
    '''
    self_func_name = 'pl'
    result = self
    current_frame = inspect.getouterframes(inspect.currentframe())[1]
    print('\n    '+gen_line_info(current_frame))

    if title:
        print(title, result)
    else:
        if auto_get_title:
            print(gen_title_from_stack_info(
                traceback.extract_stack(), self_func_name), result)
        else:
            print(result)
    return result

def ppl(self, title=None, auto_get_title=True):
    ''' pp with line information including file full path and line number.
        Notice, it will print new line firstly, since in some case, 
        there will be other string before file path
        and some editor cannot jump to the location.
    '''
    self_func_name = 'ppl'
    result = self
    current_frame = inspect.getouterframes(inspect.currentframe())[1]
    print('\n    '+gen_line_info(current_frame))

    if title:
        print(title)
    else:
        if auto_get_title:
            print(gen_title_from_stack_info(
                traceback.extract_stack(), self_func_name))
    pprint.pprint(result)
    return result

def length(self):
    return len(self)

def size(self):
    return len(self)

def flag_test_func(title=None):
    ''' p with line information including file full path and line number.
        Notice, it will print new line firstly, since in some case, 
        there will be other string before file path
        and some editor cannot jump to the location.
    '''
    msg = 'There are test codes in this place!'
    current_frame = inspect.getouterframes(inspect.currentframe())[1]
    print('\n    '+gen_line_info(current_frame))

    if title:
        print(title+":", msg)
    else:
        print(msg)
    return True

def for_test():
    print("for test")

def inject_musts_methods():
    # must use list(globals().iteritems()),
    # if just use globals().iteritems(), 
    # set_method_to_builtin(NoneType, classmethod(func), name) will not work,
    # since in iteration, globals() will change.
    if sys.version_info < (3, 0):
        globals_items = list(globals().iteritems())
    else:
        globals_items = list(globals().items())

    [set_method_to_object(func) for name, func 
        in globals_items 
        if name.startswith('must_')]
    [set_method_to_builtin(NoneType, classmethod(func), name) for name, func 
        in globals_items 
        if name.startswith('must_')]
    set_method_to_object(p)
    set_method_to_object(pp)
    set_method_to_object(pl)
    set_method_to_object(ppl)
    set_method_to_object(length)
    set_method_to_object(size)
    # for None
    set_method_to_builtin(NoneType, classmethod(p), 'p')
    set_method_to_builtin(NoneType, classmethod(pp), 'pp')
    set_method_to_builtin(NoneType, classmethod(pl), 'pl')
    set_method_to_builtin(NoneType, classmethod(ppl), 'ppl')
    # set_method_to_builtin(NoneType, classmethod(must_equal), 'must_equal')
    # set_method_to_builtin(type, p, 'p')

    # set_method_to_object(for_test)
    if sys.version_info < (3, 0):
        set_method_to_builtin(new.classobj, for_test, 'for_test')


    set_method_to_object(p_format)
    set_method_to_builtin(NoneType, classmethod(p_format), 'p_format')
    set_method_to_object(pp_format)
    set_method_to_builtin(NoneType, classmethod(pp_format), 'pp_format')
    set_method_to_object(pl_format)
    set_method_to_builtin(NoneType, classmethod(pl_format), 'pl_format')
    set_method_to_object(ppl_format)
    set_method_to_builtin(NoneType, classmethod(ppl_format), 'ppl_format')

    builtins.flag_test = flag_test_func


inject_musts_methods()

