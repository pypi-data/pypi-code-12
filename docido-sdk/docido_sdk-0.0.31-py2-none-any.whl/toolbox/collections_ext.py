import copy
import errno
import itertools
import os
import os.path as osp

from peak.util.proxies import ObjectWrapper
import yaml
from yaml import Loader

from . yaml_ext import load_all_yaml_constructors

load_all_yaml_constructors()


class nameddict(dict):
    """ Provides dictionary whose keys are accessible via the property
    syntax: `obj.key`
    """
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.__dict__ = self
        self.__namify(self.__dict__)

    def __namify(self, a_dict):
        for key in a_dict.keys():
            if type(a_dict[key]) == dict:
                a_dict[key] = nameddict(a_dict[key])

    def __setitem__(self, key, value):
        if type(value) == dict:
            value = nameddict(value)
        super(nameddict, self).__setitem__(key, value)

    def __setattr__(self, key, value):
        if key != '__dict__' and type(value) == dict:
            value = nameddict(value)
        super(nameddict, self).__setattr__(key, value)

    def __deepcopy__(self, memo):
        cls = self.__class__
        content = dict()
        for k, v in self.iteritems():
            content[k] = copy.deepcopy(v, memo)
        result = cls.__new__(cls)
        result.__init__(content)
        return result


class Configuration(nameddict):
    @classmethod
    def from_file(cls, path):
        if not osp.exists(path) and not osp.isabs(path):
            path = osp.join(osp.dirname(osp.abspath(__file__)), path)
        with open(path, 'r') as istr:
            return Configuration(yaml.load(istr, Loader=Loader))

    @classmethod
    def from_env(cls, envvar, default, default_config):
        try:
            config = Configuration.from_file(os.getenv(envvar, default))
        except IOError as e:
            if e.errno == errno.ENOENT:
                config = default_config
            else:
                raise e
        return config


class contextobj(ObjectWrapper):
    """ Proxy a Python object, and provides a stack where copies of the
    wrapped object can be manipulated with `_push` and `_pop`
    member functions.

    `contextobj` can also be used in a Python with-statement.

        >>> o = contextobj(dict())
        >>> with o:
        >>>     o['foo'] = 'bar'
        >>> # the dict has been rollbacked: it is empty again
    """
    __obj_stack = None

    def __init__(self, *args, **kwargs):
        ObjectWrapper.__init__(self, *args, **kwargs)
        self.__obj_stack = []

    def _push(self):
        if not isinstance(self.__subject__, dict):
            raise NotImplementedError()
        self.__obj_stack.append(copy.deepcopy(self.__subject__))
        return self

    def _pop(self):
        self.__subject__.clear()
        self.__subject__.update(self.__obj_stack.pop())
        return self

    def __enter__(self):
        return self._push()

    def __exit__(self, type_, value, traceback):
        self._pop()
        return False


def chunks(it, n):
    """Split an iterator into chunks with `n` elements each.
    Examples
        # n == 2
        >>> x = chunks(iter([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]), 2)
        >>> list(x)
        [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9], [10]]
        # n == 3
        >>> x = chunks(iter([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]), 3)
        >>> list(x)
        [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10]]
    """
    for first in it:
        yield [first] + list(itertools.islice(it, n - 1))
