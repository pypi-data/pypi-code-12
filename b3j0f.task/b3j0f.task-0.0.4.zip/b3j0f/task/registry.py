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

__all__ = ['Registry', 'TASK_NAME', 'TASK_ARGS', 'TASK_KWARGS']

from six import string_types

from b3j0f.utils.path import getpath
from b3j0f.conf import Configurable

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
      + kwargs: dict of task parameters.
"""

TASK_NAME = 'name'  #: task id field name in task conf
TASK_ARGS = 'args'  #: task args field name in task conf
TASK_KWARGS = 'kwargs'  #: task kwargs field name in task conf


@Configurable(paths='task.conf')
class Registry(object):
    """Task resolver."""

    def __init__(self, registry=None, *args, **kwargs):
        """
        :param registry: task registry which implements __{get; set; del}item__
            __len__, and __iter__ methods.
        """

        super(Registry, self).__init__(*args, **kwargs)

        self._registry = {} if registry is None else registry

    @property
    def registry(self):
        """Get this registry."""
        return self._registry

    @registry.setter
    def registry(self, value):
        """Change of registry in saving old tasks."""

        oldregistry, self._registry = self._registry, value

        for name in oldregistry:
            if name not in value:
                value[name] = oldregistry[name]

    def getname(self, task):
        """Get task name.

        :return: task name or None if task is not registered.
        :rtype: str"""
        result = None

        for key in self._registry:
            val = self._registry[key]
            if val is task:
                result = key
                break

        return result

    def __getitem__(self, key):

        return self._registry[key]

    def __setitem__(self, key, value):

        self._registry[key] = value

    def __delitem__(self, key):

        del self._registry[key]

    def __iter__(self):

        return iter(self._registry)

    def __contains__(self, value):

        return value in self._registry

    def __len__(self):

        return len(self._registry)

    def __bool__(self):

        return bool(self._registry)

    def clear(self):

        self._registry.clear()

    def register(self, task=None, name=None):
        """Register a task related.

        It can be used such as a decorator like :

        @register
        def task(): pass

        @register(name='mytask')
        def task(): pass

        Or like a a function :

        register(lambda : None)
        register(lambda : None, name='mytask')

        :param task: task or task name.
        :param name: task name.
        :return: registered task."""

        if task is None:
            result = self.register

        elif isinstance(task, string_types):
            name = task
            result = lambda task: self.register(task=task, name=name)

        elif callable(task):
            if name is None:
                name = getpath(task)

            self._registry[name] = task

            result = task

        else:
            raise ValueError(
                'Wrong task and {0} name {1}. callable and str Expected'.format(
                    task, name
                )
            )

        return result

    def update(self, registry):
        """Update a registry with new registry tasks."""

        for name in registry:
            self._registry[name] = registry[name]

    def register_content(self, obj):
        """Register all input object callable content.

        For example, obj can be a module."""

        for name in dir(obj):

            elt = getattr(obj, name)

            if callable(elt):
                self.register(elt)

    def get(self, conf):
        """Get a task from a configuration.

        :param conf: configuration
        :type conf: str or dict.
        :return: task with kwargs.
        :rtype: tuple"""

        if isinstance(conf, string_types):
            result = self._registry[conf], [], {}

        elif isinstance(conf, dict):
            result = (
                self._registry[conf[TASK_NAME]],
                conf.get(TASK_ARGS, []),
                conf.get(TASK_KWARGS, {})
            )

        return result

    def run(self, conf):
        """Run input configuration.

        :return: execution of input configuration."""

        task, args, kwargs = self.get(conf=conf)

        return task(*args, **kwargs)

    def conf(self, task, args=None, kwargs=None):
        """Generate a new task conf related to input task id and kwargs.

        :param task: task identifier.
        :type task: str or routine
        :param dict kwargs: task parameters.

        :return: {TASK_NAME: name, TASK_KWARGS: kwargs}
        :rtype: dict
        """

        if args is None:
            args = []

        if kwargs is None:
            kwargs = {}

        # if task is a task routine, find the corresponding task id
        if callable(task):
            task = self.getname(task)

        result = {TASK_NAME: task, TASK_ARGS: args, TASK_KWARGS: kwargs}

        return result
