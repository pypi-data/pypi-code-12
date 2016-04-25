# coding: utf-8
"""
    tests.test_core_wrappers_accepts
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    pyextend.core.wrappers.accepts test case

    :copyright: (c) 2016 by Vito.
    :license: GNU, see LICENSE for more details.
"""
import pytest
from pyextend.core.wrappers.accepts import accepts


def func_accept(f, *args, **kwargs):
    exception = TypeError if 'exception' not in kwargs else kwargs['exception']
    try:
        f(*args, **kwargs)
        return True
    except exception:
        return False


def test_accepts_single_parameter():

    def func_single_param(param_type):
        @accepts(a=param_type)
        def _func_single_param(a):
            return a
        return _func_single_param

    assert func_accept(func_single_param(int), 10) is True
    assert func_accept(func_single_param(int), []) is False
    assert func_accept(func_single_param(str), 'a') is True
    assert func_accept(func_single_param(str), 11) is False
    assert func_accept(func_single_param(list), []) is True
    assert func_accept(func_single_param(list), 'abc') is False
    assert func_accept(func_single_param(dict), {}) is True
    assert func_accept(func_single_param(dict), []) is False

    assert func_accept(func_single_param('__iter__'), 'abc') is True
    assert func_accept(func_single_param('__iter__'), (1, 2)) is True
    assert func_accept(func_single_param('__iter__'), [1, 2]) is True
    assert func_accept(func_single_param('__iter__'), {'a': 1, 'b': 2}) is True
    assert func_accept(func_single_param('__iter__'), range(10)) is True
    assert func_accept(func_single_param('__iter__'), 11) is False

    # None able parameter test
    assert func_accept(func_single_param((int, None)), None) is True
    assert func_accept(func_single_param((int, None)), 10) is True
    assert func_accept(func_single_param(('__iter__', None)), 'abc') is True
    assert func_accept(func_single_param(('__iter__', None)), None) is True


def test_accepts_multi_parameter():

    def func_multi_param(*args_types, **kwargs_types):
        kwargs_types = dict(kwargs_types, **{'arg_'+str(i): arg for i, arg in enumerate(args_types)})
        keys = sorted(kwargs_types.keys())

        def _get_params_str(**kwargs):
            """Returns kwargs to function accepts 's params"""
            def _tuple_2_str(tuple_obj):
                """Returns tuple obj to str. like (<class 'str'>, None)  --> '(str, None)'"""
                a = ','.join([str(x.__name__) for x in tuple_obj if type(x).__name__ == 'type'] +
                             ["'"+str(x)+"'" for x in tuple_obj if type(x).__name__ == 'str'] +
                             [str(x) for x in tuple_obj if type(x).__name__ not in ['type', 'str']])
                return '(' + a + ')'

            params_list = [p[0]+'='+str(p[1].__name__) for p in kwargs.items() if type(p[1]).__name__ == 'type'] + \
                          [p[0]+'='+"'"+str(p[1])+"'" for p in kwargs.items()
                           if type(p[1]).__name__ not in ['type', 'tuple']] + \
                          [p[0]+'='+_tuple_2_str(p[1]) for p in kwargs.items() if type(p[1]).__name__ == 'tuple']
            return ','.join(params_list)

        # @accepts(a=str)
        # def _func_multi_param(a):
        #     pass

        inner_func_str = """
@accepts({kwargs_types})
def _func_multi_param({keys}):
    return {keys}
""".format(kwargs_types=_get_params_str(**kwargs_types), keys=','.join(keys))

        # aaa = compile(inner_func_str, '', 'exec')

        # dynamic mount the _func_multi_param function into locals
        exec(inner_func_str, globals(), locals())
        print(globals().keys())
        print(locals())
        _func_multi_param_func = locals()['_func_multi_param']
        return _func_multi_param_func

    assert func_accept(func_multi_param(int), 10) is True
    assert func_accept(func_multi_param(int, str), 10, 'a') is True
    assert func_accept(func_multi_param(int, list), 10, []) is True
    assert func_accept(func_multi_param(int, list, str), 10, [], 'a') is True
    assert func_accept(func_multi_param(int, list, (dict, None)), 10, [], {}) is True
    assert func_accept(func_multi_param(dict, list, ('__iter__', None)), {}, [], None) is True
    assert func_accept(func_multi_param(dict, list, ('__iter__', None)), {}, [], 'ABC') is True
    assert func_accept(func_multi_param(dict, list, (int, None)), {}, [], 11) is True
    assert func_accept(func_multi_param(dict, list, (int, None)), {}, [], None) is True
    assert func_accept(func_multi_param(dict, list, (int, None)), {}, [], []) is False
    assert func_accept(func_multi_param('__iter__'), []) is True
    assert func_accept(func_multi_param(('__iter__', int)), None) is False


if __name__ == '__main__':
    pytest.main(__file__)
