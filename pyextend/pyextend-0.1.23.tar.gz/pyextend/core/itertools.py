# coding: utf-8
"""
    pyextend.core.itertools
    ~~~~~~~~~~~~~~~~~~~~~
    pyextend core string extension tools

    :copyright: (c) 2016 by Vito.
    :license: GNU, see LICENSE for more details.
"""

__all__ = ['unpack', 'merge']


# from pyextend.core.wrappers import accepts
from .wrappers import accepts


@accepts(iterable='__iter__', count=int)
def unpack(iterable, count, fill=None):
    """
    The iter data unpack function.

    Example 1:
        In[1]: source = 'abc'
        In[2]: a, b = safe_unpack(source, 2)
        In[3]: print(a, b)
        a b

    Example 2:
        In[1]: source = 'abc'
        In[2]: a, b, c, d = safe_unpack(source, 4)
        In[3]: print(a, b, c, d)
        a b None None
    """
    iterable = list(enumerate(iterable))
    cnt = count if count <= len(iterable) else len(iterable)
    results = [iterable[i][1] for i in range(cnt)]

    # results[len(results):len(results)] = [fill for i in range(count-cnt)]
    results = merge(results, [fill for i in range(count-cnt)])
    return tuple(results)


@accepts(iterable1='__iter__')
def merge(iterable1, *args):
    """
    Returns an type of iterable1 value, which merged after iterable1 used *args

    :exception TypeError: if any parameter type of args not equals type(iterable1)

    Example 1:
        source = ['a', 'b', 'c']
        result = merge(source, [1, 2, 3])
        self.assertEqual(result, ['a', 'b', 'c', 1, 2, 3])

        result = merge(source, [1, 2, 3], ['x', 'y', 'z'])
        self.assertEqual(result, ['a', 'b', 'c', 1, 2, 3, 'x', 'y', 'z'])

    Example 2:
        source = 'abc'
        result = merge(source, '123')
        self.assertEqual(result, 'abc123')

        result = merge(source, '123', 'xyz')
        self.assertEqual(result, 'abc123xyz')

    Example 3:
        source = ('a', 'b', 'c')
        result = merge(source, (1, 2, 3))
        self.assertEqual(result, ('a', 'b', 'c', 1, 2, 3))

        result = merge(source, (1, 2, 3), ('x', 'y', 'z'))
        self.assertEqual(result, ('a', 'b', 'c', 1, 2, 3, 'x', 'y', 'z'))

    Example 4:
        source = {'a': 1, 'b': 2, 'c': 3}
        result = merge(source, {'x': 'm', 'y': 'n'}, {'z': '1'})
        self.assertEqual(result, {'a': 1, 'b': 2, 'c': 3, 'x': 'm', 'y': 'n', 'z': '1'})

    """

    result_list = list(iterable1) if not isinstance(iterable1, dict) else eval('list(iterable1.items())')

    for i, other in enumerate(args, start=1):
        if not isinstance(other, type(iterable1)):
            raise TypeError('the parameter type of index {} not equals type of index 0'.format(i))
        if not isinstance(other, dict):
            result_list[len(result_list):len(result_list)] = list(other)
        else:
            result_list[len(result_list):len(result_list)] = list(other.items())

    if isinstance(iterable1, str):
        return ''.join(result_list)
    elif isinstance(iterable1, tuple):
        return tuple(result_list)
    elif isinstance(iterable1, dict):
        return dict(result_list)
    else:
        return result_list
