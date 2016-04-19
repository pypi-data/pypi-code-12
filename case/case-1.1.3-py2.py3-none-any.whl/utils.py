from __future__ import absolute_import, unicode_literals

import functools
import importlib
import inspect
import io
import logging
import sys

from contextlib import contextmanager
from six import reraise, string_types

__all__ = [
    'WhateverIO', 'decorator', 'get_logger_handlers',
    'noop', 'symbol_by_name',
]

StringIO = io.StringIO
_SIO_write = StringIO.write
_SIO_init = StringIO.__init__


def update_wrapper(wrapper, wrapped, *args, **kwargs):
    wrapper = functools.update_wrapper(wrapper, wrapped, *args, **kwargs)
    wrapper.__wrapped__ = wrapped
    return wrapper


def wraps(wrapped,
          assigned=functools.WRAPPER_ASSIGNMENTS,
          updated=functools.WRAPPER_UPDATES):
    return functools.partial(update_wrapper, wrapped=wrapped,
                             assigned=assigned, updated=updated)


class _CallableContext(object):

    def __init__(self, context, cargs, ckwargs, fun):
        self.context = context
        self.cargs = cargs
        self.ckwargs = ckwargs
        self.fun = fun

    def __call__(self, *args, **kwargs):
        return self.fun(*args, **kwargs)

    def __enter__(self):
        self.ctx = self.context(*self.cargs, **self.ckwargs)
        return self.ctx.__enter__()

    def __exit__(self, *einfo):
        if self.ctx:
            return self.ctx.__exit__(*einfo)


def decorator(predicate):
    context = contextmanager(predicate)

    @wraps(predicate)
    def take_arguments(*pargs, **pkwargs):

        @wraps(predicate)
        def decorator(cls):
            if inspect.isclass(cls):
                orig_setup = cls.setUp
                orig_teardown = cls.tearDown

                @wraps(cls.setUp)
                def around_setup(*args, **kwargs):
                    try:
                        contexts = args[0].__rb3dc_contexts__
                    except AttributeError:
                        contexts = args[0].__rb3dc_contexts__ = []
                    p = context(*pargs, **pkwargs)
                    p.__enter__()
                    contexts.append(p)
                    return orig_setup(*args, **kwargs)
                around_setup.__wrapped__ = cls.setUp
                cls.setUp = around_setup

                @wraps(cls.tearDown)
                def around_teardown(*args, **kwargs):
                    try:
                        contexts = args[0].__rb3dc_contexts__
                    except AttributeError:
                        pass
                    else:
                        for context in contexts:
                            context.__exit__(*sys.exc_info())
                    orig_teardown(*args, **kwargs)
                around_teardown.__wrapped__ = cls.tearDown
                cls.tearDown = around_teardown

                return cls
            else:
                @wraps(cls)
                def around_case(self, *args, **kwargs):
                    with context(*pargs, **pkwargs) as context_args:
                        context_args = context_args or ()
                        if not isinstance(context_args, tuple):
                            context_args = (context_args,)
                        return cls(*(self,) + args + context_args, **kwargs)
                return around_case

        if len(pargs) == 1 and callable(pargs[0]):
            fun, pargs = pargs[0], ()
            return decorator(fun)
        return _CallableContext(context, pargs, pkwargs, decorator)
    assert take_arguments.__wrapped__
    return take_arguments


def get_logger_handlers(logger):
    return [
        h for h in logger.handlers
        if not isinstance(h, logging.NullHandler)
    ]


def symbol_by_name(name, aliases={}, imp=None, package=None,
                   sep='.', default=None, **kwargs):
    """Get symbol by qualified name.

    The name should be the full dot-separated path to the class::

        modulename.ClassName

    Example::

        celery.concurrency.processes.TaskPool
                                    ^- class name

    or using ':' to separate module and symbol::

        celery.concurrency.processes:TaskPool

    If `aliases` is provided, a dict containing short name/long name
    mappings, the name is looked up in the aliases first.

    Examples:

        >>> symbol_by_name('celery.concurrency.processes.TaskPool')
        <class 'celery.concurrency.processes.TaskPool'>

        >>> symbol_by_name('default', {
        ...     'default': 'celery.concurrency.processes.TaskPool'})
        <class 'celery.concurrency.processes.TaskPool'>

        # Does not try to look up non-string names.
        >>> from celery.concurrency.processes import TaskPool
        >>> symbol_by_name(TaskPool) is TaskPool
        True

    """
    if imp is None:
        imp = importlib.import_module

    if not isinstance(name, string_types):
        return name                                 # already a class

    name = aliases.get(name) or name
    sep = ':' if ':' in name else sep
    module_name, _, cls_name = name.rpartition(sep)
    if not module_name:
        cls_name, module_name = None, package if package else cls_name
    try:
        try:
            module = imp(module_name, package=package, **kwargs)
        except ValueError as exc:
            reraise(ValueError,
                    ValueError("Couldn't import {0!r}: {1}".format(name, exc)),
                    sys.exc_info()[2])
        return getattr(module, cls_name) if cls_name else module
    except (ImportError, AttributeError):
        if default is None:
            raise
    return default


class WhateverIO(StringIO):

    def __init__(self, v=None, *a, **kw):
        _SIO_init(self, v.decode() if isinstance(v, bytes) else v, *a, **kw)

    def write(self, data):
        _SIO_write(self, data.decode() if isinstance(data, bytes) else data)


def noop(*args, **kwargs):
    pass
