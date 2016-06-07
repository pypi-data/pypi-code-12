#!/usr/bin/env python
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

from unittest import TestCase, main

from b3j0f.utils.ut import UTCase

from b3j0f.utils.path import getpath
from ..registry import TASK_PARAMS, TASK_NAME, Registry


def test_exception(**kwargs):

    raise Exception()

COUNT = 'count'


class RegistryTest(UTCase):

    def setUp(self):

        self.registry = Registry()

class TaskUnregisterTest(RegistryTest):
    """Test unregister_tasks function"""

    def setUp(self):
        """Create two tasks for future unregistration."""

        super(TaskUnregisterTest, self).setUp()

        # clear dico and add only self names
        self.names = 'a', 'b'
        for name in self.names:
            self.registry.register(name=name, task=lambda: None)

    def test_unregister(self):
        """Unregister one by one"""

        for name in self.names:
            del self.registry[name]
            self.assertNotIn(name, self.registry)

    def test_unregister_clear(self):
        """Unregister all tasks with an empty parameter."""

        self.registry.clear()
        self.assertFalse(self.registry)


class TaskRegistrationTest(RegistryTest):
    """Test to register tasks."""

    def setUp(self):
        # clean task paths

        super(TaskRegistrationTest, self).setUp()

        self.tasks = {
            'a': lambda: None, 'b': lambda: None, 'c': lambda: None
        }
        self.registry = Registry()
        self.registry.update(self.tasks)

    def test_register(self):
        """Check for registered task in registered tasks"""

        for task in self.tasks:
            self.assertIn(task, self.registry)


class GetTaskTest(RegistryTest):
    """Test get task function."""

    def test_get_unregisteredtask(self):
        """Test to get unregistered task."""

        getTaskTest = getpath(GetTaskTest)
        self.registry.register(name=getTaskTest, task=GetTaskTest)
        task, _ = self.registry.get(getTaskTest)
        self.assertEqual(task, GetTaskTest)

    def test_get_registeredtask(self):
        """Test to get registered task."""

        _id = 'a'
        self.registry.register(name=_id, task=GetTaskTest)
        task, _ = self.registry.get(_id)
        self.assertEqual(task, GetTaskTest)


class TaskRegistrationDecoratorTest(RegistryTest):
    """Test registration decorator"""

    def test_register_without_parameters(self):

        def register():
            pass
        self.registry.register()(register)
        self.assertIn(getpath(register), self.registry)

    def test_register(self):

        @self.registry.register()
        def register():
            pass
        self.assertIn(getpath(register), self.registry)

    def test_registername(self):

        _id = 'toto'

        @self.registry.register(_id)
        def register():
            pass
        self.assertIn(_id, self.registry)


class GetTaskWithParamsTest(RegistryTest):
    """Test get task with params function."""

    def setUp(self):

        super(GetTaskWithParamsTest, self).setUp()

        self.wrong_function = 'test.test'

        self.existing_function = getpath(open)

        self.registry.register(open)

    def test_none_task_from_str(self):

        conf = self.wrong_function

        self.assertRaises(KeyError, self.registry.get, conf=conf)

    def test_none_task_from_dict(self):

        conf = {TASK_NAME: self.wrong_function}

        self.assertRaises(KeyError, self.registry.get, conf=conf)

    def test_task_from_str(self):

        conf = self.existing_function

        task, params = self.registry.get(conf=conf)

        self.assertEqual((task, params), (open, {}))

    def test_task_from_dict(self):

        conf = {TASK_NAME: self.existing_function}

        task, params = self.registry.get(conf=conf)

        self.assertEqual((task, params), (open, {}))

    def test_task_from_dict_with_params(self):

        param = {'a': 1}

        conf = {
            TASK_NAME: self.existing_function,
            TASK_PARAMS: param}

        task, params = self.registry.get(conf=conf)

        self.assertEqual((task, params), (open, param))

    def test_cache(self):

        conf = self.existing_function

        task_not_cached_0, _ = self.registry.get(conf=conf)

        task_not_cached_1, _ = self.registry.get(conf=conf)

        self.assertTrue(task_not_cached_0 is task_not_cached_1)

        task_cached_0, _ = self.registry.get(conf=conf)

        task_cached_1, _ = self.registry.get(conf=conf)

        self.assertTrue(task_cached_0 is task_cached_1)


class RunTaskTest(RegistryTest):
    """Test run task."""

    def setUp(self):

        super(RunTaskTest, self).setUp()

        @self.registry.register('test')
        def test(**kwargs):
            return self

        @self.registry.register('test_exception')
        def test_exception(**kwargs):
            raise Exception()

        @self.registry.register('test_params')
        def test_params(ctx, **kwargs):
            return kwargs['a'] + kwargs['b'] + ctx['a'] + 1

    def test_simple(self):
        """Test simple task."""

        result = self.registry.run('test')
        self.assertIs(result, self)

    def test_exception(self):
        """Test task which raises an exception."""

        self.assertRaises(Exception, self.registry.run, 'test_exception')

    def test_simple_params(self):
        """Test task with params"""

        conf = self.registry.conf(
            'test_params', {'a': 1, 'b': 2, 'ctx': {'a': 1}}
        )
        result = self.registry.run(conf)
        self.assertEqual(result, 5)


class NewConfTest(RegistryTest):
    """Test new conf."""

    def test_id(self):
        """Test to generate a new conf with only an id."""

        conf = self.registry.conf('a')
        self.assertEqual(conf, {TASK_NAME: 'a', TASK_PARAMS: {}})

    def test_with_empty_params(self):
        """Test to generate a new conf with empty params."""

        conf = self.registry.conf('a', {})

        self.assertEqual(conf, {TASK_NAME: 'a', TASK_PARAMS: {}})

    def test_with_params(self):
        """Test to generate a new conf with params."""

        params = {'a': 1}
        conf = self.registry.conf('a', params)

        self.assertEqual(conf[TASK_NAME], 'a')
        self.assertEqual(conf[TASK_PARAMS], params)

    def test_with_routine(self):
        """Test to generate a new conf related to a task routine."""

        self.registry.register(open)

        conf = self.registry.conf(open)

        self.assertEqual(conf['name'], getpath(open))

    def test_with_routine_and_params(self):
        """Test to generate a new conf related to a task routine and params."""

        self.registry.register(open)

        params = {'a': 1}
        conf = self.registry.conf(open, params)

        self.assertEqual(conf[TASK_NAME], getpath(open))
        self.assertEqual(conf[TASK_PARAMS], params)


if __name__ == '__main__':
    main()
