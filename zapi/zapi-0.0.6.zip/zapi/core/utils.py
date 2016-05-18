__author__ = 'zhonghong'

import os
import re
import imp
import string
import logging

log = logging.getLogger(__name__)



class FlyweightMixin(object):
    _instances = dict()
    def __init__(self, *args, **kwargs):
        raise NotImplementedError

    def __new__(cls, *args, **kwargs):
        return cls._instances.setdefault(
                    (cls, args, tuple(kwargs.items())),
                    super(type(cls), cls).__new__(cls, *args, **kwargs))


def normalize_name(name):
    """
    Converts camel-case style names into underscore seperated words. Example::

        >>> normalize_name('oneTwoThree')
        'one_two_three'
        >>> normalize_name('FourFiveSix')
        'four_five_six'

    """
    new = re.sub('(((?<=[a-z])[A-Z])|([A-Z](?![A-Z]|$)))', '_\\1', name)
    return new.lower().strip('_')


def capitalize_name(name):
    """
    Converts underscore seperated names into capitalize style words. Example::

        >>> normalize_name('one_two_three')
        'OneTwoThree'

    """
    return string.capwords(name, '_').replace('_', '')


def load_module(mod_dir, check_callable=True):
    """
    @note: Load execution modules
    @param mod_dir: module dir
    @return: module list
    """
    names = {}
    modules = []
    objects = {}
    for fn_ in os.listdir(mod_dir):
        if fn_.startswith('_'):
            continue
        if (fn_.endswith(('.py', '.pyc', '.pyo', '.so')) or os.path.isdir(fn_)):
            extpos = fn_.rfind('.')
            if extpos > 0:
                _name = fn_[:extpos]
            else:
                _name = fn_
            names[_name] = os.path.join(mod_dir, fn_)
    for name in names:
        try:
            # the second arg of find_module function must be list, otherwise function call will failed.
            fn_, path, desc = imp.find_module(name, [mod_dir])
            mod = imp.load_module(name, fn_, path, desc)
        except Exception as e:
            log.error(e)
            continue
        modules.append(mod)
    for mod in modules:
        for attr in dir(mod):
            if attr.startswith('_'):
                continue
            if check_callable:
                if callable(getattr(mod, attr)):
                    obj = getattr(mod, attr)
                    if isinstance(obj, type):
                        if any(['Error' in obj.__name__, 'Exception' in obj.__name__]):
                            continue
                    try:
                        objects['{0}.{1}'.format(mod.__name__, normalize_name(attr))] = obj
                    except:
                        continue
            else:
                obj = getattr(mod, attr)
                objects['{0}.{1}'.format(mod.__name__, attr)] = obj

    return objects



# print load_module('E:/python_project/tmp-dev/codesnippet/zapi/application/config', False)
