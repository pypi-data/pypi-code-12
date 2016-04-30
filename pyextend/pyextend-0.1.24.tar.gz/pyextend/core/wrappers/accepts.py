# coding: utf-8
"""
    pyextend.core.wrappers.accepts
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    pyextend core wrappers accepts wrapper

    :copyright: (c) 2016 by Vito.
    :license: GNU, see LICENSE for more details.
"""

import functools
from .system import version_info


def accepts(exception=TypeError, **types):
    """
    A wrapper of function for checking function parameters type

    Example 1:
        @accepts(a=int, b='__iter__', c=str)
        def test(a, b=None, c=None):
            print('accepts OK')

        test(13, b=[], c='abc')  -- OK
        test('aaa', b=(), c='abc') --Failed

    Example 2:
        @accepts(a=int, b=('__iter__', None), c=str)
        def test(a, b=None, c=None):
            print('accepts OK')

        test(13, b=[], c='abc')  -- OK
        test(13, b=None, c='abc')  -- OK

    """

    def check_param(v, type_or_funcname):
        if isinstance(type_or_funcname, tuple):
            results1 = [check_param(v, t) for t in type_or_funcname if t is not None]
            results2 = [v == t for t in type_or_funcname if t is None]
            return any(results1) or any(results2)

        is_type_instance, is_func_like = False, False
        try:
            is_type_instance = isinstance(v, type_or_funcname)
        except TypeError:
            pass
        if isinstance(type_or_funcname, str):
            if type_or_funcname == '__iter__' and isinstance(v, str) and version_info < (3,):
                # at py 2.x, str object has non `__iter__` attribute,
                # str object can use like `for c in s`, bcz `iter(s)` returns an iterable object.
                is_func_like = True
            else:
                is_func_like = hasattr(v, type_or_funcname)

        return is_type_instance or is_func_like

    def check_accepts(f):
        assert len(types) <= f.__code__.co_argcount,\
            'accept number of arguments not equal with function number of arguments in "{}"'.format(f.__name__)

        @functools.wraps(f)
        def new_f(*args, **kwargs):
            for i, v in enumerate(args):
                if f.__code__.co_varnames[i] in types and \
                        not check_param(v, types[f.__code__.co_varnames[i]]):
                    raise exception("function '%s' arg '%s'=%r does not match %s" %
                                    (f.__name__, f.__code__.co_varnames[i], v, types[f.__code__.co_varnames[i]]))
                    del types[f.__code__.co_varnames[i]]

            for k, v in kwargs.items():
                if k in types and \
                        not check_param(v, types[k]):
                    raise exception("function '%s' arg '%s'=%r does not match %s" % (f.__name__, k, v, types[k]))
            return f(*args, **kwargs)
        return new_f
    return check_accepts
