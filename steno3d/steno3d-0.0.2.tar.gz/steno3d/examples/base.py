"""base.py sets up BaseExample class that allows examples to be accessed
as properties at the class level
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from os.path import realpath
from os.path import sep

from future.utils import with_metaclass


class exampleproperty(object):
    """wrapper that sets class method as saved property"""

    def __init__(self, func):
        self.func = classmethod(func)
        self.propname = '_' + func.__name__

    def __get__(self, cls, owner):
        if getattr(owner, self.propname, None) is None:
            setattr(owner, self.propname, self.func.__get__(None, owner)())
        return getattr(owner, self.propname)


class exampleoutput(object):
    """wrapper that sets class method to remove saved properties"""

    def __init__(self, func, directory):
        self.func = classmethod(func)
        self._directory = ['_' + prop for prop in directory]
        self._stash = [None for prop in directory]

    def __get__(self, cls, owner):
        def _output():
            """return the original function surrounded by stash and unstash"""
            self.stash(owner)
            out = self.func.__get__(None, owner)()
            self.unstash(owner)
            return out
        return _output

    def stash(self, owner):
        """stash saved properties during example output"""
        for i, prop in enumerate(self._directory):
            self._stash[i] = getattr(owner, prop, None)
            setattr(owner, prop, None)

    def unstash(self, owner):
        """unstash saved properties after example output"""
        for i, prop in enumerate(self._directory):
            setattr(owner, prop, self._stash[i])


class _ExampleMetaClass(type):
    """metaclass that wraps every function with exampleproperty()"""

    def __new__(mcs, name, bases, attrs):
        if name not in ('BaseExample', 'Images'):
            assert ('get_resources' in attrs and
                    callable(attrs['get_resources'])), \
                'Example {cls} class must have method get_resources()'.format(
                    cls=name
                )
            assert ('get_project' in attrs and
                    callable(attrs['get_project'])), \
                'Example class {cls} must have method get_project()'.format(
                    cls=name
                )

        example_directory = []
        for attr in attrs:
            value = attrs[attr]
            if not attr.startswith('get_') and callable(value):
                attrs[attr] = exampleproperty(value)
                example_directory.append(attr)

        for attr in attrs:
            value = attrs[attr]
            if attr.startswith('get_') and callable(value):
                attrs[attr] = exampleoutput(value, example_directory)

        return type.__new__(mcs, name, bases, attrs)


class BaseExample(with_metaclass(_ExampleMetaClass, object)):
    """basic class that all examples inherit from"""

    def __init__(self, *args, **kwargs):
        raise TypeError('Examples cannot be instantiated. Please access '
                        'the properties directly.')

    def asset_dir(self):
        """path to directory containing all assets"""
        return sep.join(realpath(__file__).split(sep)[:-3] + ['assets'])
