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

from time import time

from dateutil import rrule

from datetime import datetime
from ..core import register
from ..condition import (
    _any, _all, during, _not, condition, switch, STATEMENT
)
from ..registry import TASK_NAME, TASK_PARAMS


@register('error')
def condition_raise(**kwargs):
    raise Exception()


@register('true')
def condition_true(**kwargs):
    return True


@register('false')
def condition_false(**kwargs):
    return False


class DuringTest(TestCase):
    """Test during test."""

    def test_inside(self):
        duration = {"seconds": 5}
        now = time()
        now = datetime.fromtimestamp(now)
        rrule_p = {"freq": rrule.DAILY, "dtstart": now}
        result = during(rrule=rrule_p, duration=duration)
        self.assertTrue(result)

    def test_outside(self):
        now = time()
        now = datetime.fromtimestamp(now + 5)
        rrule_p = {"freq": rrule.DAILY, "dtstart": now}
        result = during(rrule=rrule_p)
        self.assertFalse(result)


class AnyTest(TestCase):
    """Test _any function."""

    def test_empty(self):
        result = _any()
        self.assertFalse(result)

    def test_unary(self):
        confs = ["true"]
        result = _any(confs=confs)
        self.assertTrue(result)

    def test_false(self):
        confs = ["false", "false"]
        result = _any(confs=confs)
        self.assertFalse(result)

    def test_true(self):
        confs = ["false", "true", "true"]
        result = _any(confs=confs)
        self.assertTrue(result)

    def test_all_true(self):
        confs = ["true", "true", "true"]
        result = _any(confs=confs)
        self.assertTrue(result)

    def test_raise(self):
        confs = ["error"]
        self.assertRaises(Exception, _any, confs=confs)


class AllTest(TestCase):
    """Test _all function."""

    def test_empty(self):
        result = _all()
        self.assertFalse(result)

    def test_unary(self):
        confs = ["true"]
        result = _all(confs=confs)
        self.assertTrue(result)

    def test_false(self):
        confs = ["false", "true", "false"]
        result = _all(confs=confs)
        self.assertFalse(result)

    def test_true(self):
        confs = ["true", "true", "true"]
        result = _all(confs=confs)
        self.assertTrue(result)

    def test_raise(self):
        confs = ["error"]
        self.assertRaises(Exception, _all, confs=confs)


class NotTest(TestCase):
    """Test _not operator."""

    def test_empty(self):
        """Test empty condition."""

        result = _not()
        self.assertTrue(result)

    def test_false(self):
        """Test true condition."""

        result = _not(condition='true')
        self.assertFalse(result)

    def test_true(self):
        """Test false condition."""

        result = _not(condition='false')
        self.assertTrue(result)

    def test_error(self):
        """Test error condition."""

        self.assertRaises(Exception, _not, condition='error')


class ConditionTest(TestCase):
    """Test condition task."""

    def setUp(self):

        self.count = 0
        register('count')(self._count)
        register('-count')(self._else_count)

    def _count(self, **kwargs):
        """Statement related to checked condition."""

        self.count += 1
        return self

    def _else_count(self, **kwargs):
        """Statement related to unchecked condition."""

        self.count -= 1
        return self

    def test_empty(self):
        """Test condition with no params"""

        result = condition()
        self.assertIsNone(result)
        self.assertEqual(self.count, 0)

    def test_empty_condition(self):
        """Test with an empty condition."""

        result = condition(statement='count', _else='-count')
        self.assertIs(result, self)
        self.assertEqual(self.count, -1)

    def test_empty_action(self):
        """Test with an empty statement."""

        result = condition(condition='true', _else='-count')
        self.assertIsNone(result)
        self.assertEqual(self.count, 0)

    def test_false(self):
        """Test with a false condition."""

        result = condition(
            condition='false', statement='count', _else='-count'
        )
        self.assertIs(result, self)
        self.assertEqual(self.count, -1)

    def test_true(self):
        """Test with a true condition."""

        result = condition(condition='true', statement='count', _else='-count')
        self.assertIs(result, self)
        self.assertEqual(self.count, 1)

    def test_error_condition(self):
        """Test with an error condition."""

        self.assertRaises(Exception, condition, condition='error')

    def test_error_statement(self):
        """Test with an error statement."""

        self.assertRaises(
            Exception, condition, condition='true', statement='error'
        )

    def test_error_else(self):
        """Test with an errored else statement."""

        self.assertRaises(
            Exception,
            condition,
            condition='true',
            statement='error',
            _else='-count'
        )


class SwitchTest(TestCase):
    """Test switch function."""

    def setUp(self):

        self.count_by_indexes = {'default': 0}
        register('count')(self._count)

    def _count(self, index='default', **kwargs):

        self.count_by_indexes[index] += 1
        return self

    def _generate_conf(self, ids):
        """Generate a conf of size items and with true indexes.

        :param list ids: ids to generate."""

        result = [
            {
                TASK_NAME: value,
                STATEMENT: {
                    TASK_NAME: 'count',
                    TASK_PARAMS: {'index': i}
                }
            }
            for i, value in enumerate(ids)
        ]
        # initialize count by indexes
        self.count_by_indexes.update({i: 0 for i in range(len(ids))})

        return result

    def test_empty_switch(self):
        """Test empty switch."""

        result = switch()
        self.assertIsNone(result, None)

    def test_empty_switch_with_default(self):
        """Test empty switch."""

        result = switch(_default='count')
        self.assertIs(result, self)

    def test_one_true_statement(self):
        """Test a switch with one statement."""

        confs = self._generate_conf(['true'])
        switch(confs=confs)
        self.assertEqual(self.count_by_indexes[0], 1)

    def test_one_false_statement(self):
        """Test a switch with one statement."""

        confs = self._generate_conf(['false'])
        switch(confs=confs)
        self.assertEqual(self.count_by_indexes[0], 0)

    def test_one_false_statement_with_default(self):
        """Test a switch with one statement."""

        confs = self._generate_conf(['false'])
        switch(confs=confs, _default='count')
        self.assertEqual(self.count_by_indexes[0], 0)
        self.assertEqual(self.count_by_indexes['default'], 1)

    def test_one_error_statement(self):
        """Test a switch with one statement."""

        confs = self._generate_conf(['error'])
        self.assertRaises(Exception, switch, confs)

    def test_statements(self):

        confs = self._generate_conf(['false', 'true', 'error'])

        switch(confs=confs)
        self.assertEqual(self.count_by_indexes[0], 0)
        self.assertEqual(self.count_by_indexes[1], 1)
        self.assertEqual(self.count_by_indexes[2], 0)

    def test_remain_statements(self):

        confs = self._generate_conf(['false', 'true', 'false'])
        switch(confs=confs, remain=True, _default='count')
        self.assertEqual(self.count_by_indexes[0], 0)
        self.assertEqual(self.count_by_indexes[1], 1)
        self.assertEqual(self.count_by_indexes[2], 1)
        self.assertEqual(self.count_by_indexes['default'], 1)

    def test_remain_error_statements(self):

        confs = self._generate_conf(['false', 'true', 'error'])
        switch(confs=confs, remain=True)
        self.assertEqual(self.count_by_indexes[0], 0)
        self.assertEqual(self.count_by_indexes[1], 1)
        self.assertEqual(self.count_by_indexes[2], 1)

    def test_all_statements(self):

        confs = self._generate_conf(['true', 'false', 'true'])
        switch(confs=confs, all_checked=True, _default='count')
        self.assertEqual(self.count_by_indexes[0], 1)
        self.assertEqual(self.count_by_indexes[1], 0)
        self.assertEqual(self.count_by_indexes[2], 1)
        self.assertEqual(self.count_by_indexes['default'], 1)

    def test_all_error_statements(self):

        confs = self._generate_conf(['false', 'true', 'error'])
        self.assertRaises(Exception, switch, confs=confs, all_checked=True)


if __name__ == '__main__':
    main()
