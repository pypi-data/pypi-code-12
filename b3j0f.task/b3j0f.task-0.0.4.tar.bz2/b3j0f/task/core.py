# -*- coding: utf-8 -*-
# --------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2016 Jonathan Labéjof <jonathan.labejof@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# --------------------------------------------------------------------

__all__ = [
    'register', 'unregister', 'getregistry', 'get', 'setregistry', 'run',
    'conf', 'register_content'
    ]

from .registry import Registry

"""Task module.

Provides tools to process tasks.

A task uses a python function. Therefore it is possible to use an absolute
path, an id or to register a function in tasks with the function/decorator
``register``. The related function may take in parameter a dict ``ctx``
which exists on a task life and a ``**kwargs`` which
contains parameters filled related to task parameters.

A task respects those types::
   - str: task name to execute.
   - dict:
      + id: task name to execute.
      + params: dict of task parameters.
"""

_REGISTRY = Registry()


def register(task=None, name=None):
    """Register a task.

    It can be used such as a decorator like :

    @register
    def task(): pass

    @register('mytask')
    def task(): pass

    Or like a a function :

    register(lambda : None)
    register(lambda : None, name='mytask')
    """

    return _REGISTRY.register(task=task, name=name)


register(register)  # save the function register.


@register
def gettask(name):

    return _REGISTRY[name]


@register
def get(conf):
    """Get a task.

    :param conf: str or dict.
    :return: task with keywords
    :rtype: tuple"""

    return _REGISTRY.get(conf)


@register
def unregister(*names):
    """
    Unregister input ids. If ids is empty, clear all registered tasks.

    :param tuple ids: tuple of task ids
    """

    for name in names:
        del _REGISTRY[name]


@register
def getregistry():
    """Get default registry."""

    return _REGISTRY


@register
def setregistry(registry):
    """Set a new registry in saving old tasks."""

    _REGISTRY.registry = registry


@register
def get(conf):
    """Get a task from a configuration.

    :param conf: configuration
    :type conf: str or dict.
    :return: task with params.
    :rtype: tuple"""

    return _REGISTRY.get(conf)


@register
def run(conf):
    """Run input configuration.

    :return: execution of input configuration."""

    return _REGISTRY.run(conf)


@register
def conf(task, args, kwargs):
    """Generate a new task conf related to input task id and params.

    :param task: task identifier.
    :type task: str or routine
    :param dict params: task parameters.

    :return: {TASK_NAME: name, TASK_PARAMS: params}
    :rtype: dict"""

    return _REGISTRY.conf(task, args, kwargs)


@register
def register_content(obj):
        """Register all input object callable content.

        For example, obj can be a module."""

        _REGISTRY.register_content(obj)
