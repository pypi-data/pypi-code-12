# This file is part of the Online Services test tools
#
# Copyright 2014 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 3, as published by the
# Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranties of MERCHANTABILITY,
# SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest


from olstests import (
    assertions,
    fixtures,
    scenarii,
)


class TestApplyScenario(unittest.TestCase):

    def test_simple_scenario_applied(self):
        t = fixtures.make_case()
        clone = scenarii.apply_scenario(t, ('scenario', dict(a=1, b='c')))
        self.assertEqual('olstests.fixtures.UnittestTest.test_pass(scenario)',
                         clone.id())
        self.assertEqual(1, clone.a)
        self.assertEqual('c', clone.b)


class TestApplyScenarios(unittest.TestCase):

    def test_apply_empty_scenarios(self):
        t = fixtures.make_case()
        self.assertEqual([], list(scenarii.apply_scenarios(t, [])))

    def test_apply_scenarios(self):
        t = fixtures.make_case()
        clones = list(scenarii.apply_scenarios(t,
                                               [('one', dict(x=1)),
                                                ('two', dict(x=2))]))
        assertions.assertLength(self, 2, clones)
        self.assertEqual('olstests.fixtures.UnittestTest.test_pass(one)',
                         clones[0].id())
        self.assertEqual(1, clones[0].x)
        self.assertEqual('olstests.fixtures.UnittestTest.test_pass(two)',
                         clones[1].id())
        self.assertEqual(2, clones[1].x)


class TestMultiplySuite(unittest.TestCase):

    def assertTestNames(self, expected, tests):

        def remove_prefix(test):
            return test.id()[len('olstests.fixtures.UnittestTest.'):]

        self.assertEqual(expected, [remove_prefix(t) for t in tests])

    def test_multiply_single_test(self):
        scenarios = [('one', dict(x=1)), ('two', dict(x=2))]
        # It's a single test but it still needs to be part of a suite to fit
        # the API.
        suite = fixtures.make_suite(['pass'])
        clones = scenarii.multiply_suite(suite, scenarios)
        self.assertTestNames(['test_pass(one)', 'test_pass(two)'], clones)

    def test_multiply_suite(self):
        suite = fixtures.make_suite(['pass', 'fail', 'error'])
        scenarios = [('one', dict(x=1)), ('two', dict(x=2))]
        clones = scenarii.multiply_suite(suite, scenarios)
        self.assertTestNames(['test_pass(one)', 'test_pass(two)',
                              'test_fail(one)', 'test_fail(two)',
                              'test_error(one)', 'test_error(two)'],
                             clones)

    def test_multiply_suite_of_suite(self):
        suite = fixtures.make_suite(['pass', 'fail', 'error'])
        super_suite = unittest.TestSuite([suite])
        scenarios = [('one', dict(x=1)), ('two', dict(x=2))]
        clones = scenarii.multiply_suite(super_suite, scenarios)
        self.assertTestNames(['test_pass(one)', 'test_pass(two)',
                              'test_fail(one)', 'test_fail(two)',
                              'test_error(one)', 'test_error(two)'],
                             clones)

    def test_multiply_test_with_scenarios(self):
        t = fixtures.make_case()
        t.scenarios = [('one', dict(x=1)), ('two', dict(x=2))]
        suite = unittest.TestSuite([t])
        clones = scenarii.multiply_suite(suite)
        # We've found the test scenarios
        self.assertTestNames(['test_pass(one)', 'test_pass(two)'], clones)

    def test_multiply_suite_with_scenarios(self):
        suite = fixtures.make_suite(['pass'])
        suite.scenarios = [('one', dict(x=1)), ('two', dict(x=2))]
        clones = scenarii.multiply_suite(suite)
        # We've used the suite scenarios
        self.assertTestNames(['test_pass(one)', 'test_pass(two)'], clones)

    def test_multiply_suite_and_test_with_scenarios(self):
        t = fixtures.make_case()
        t.scenarios = [('one', dict(x=1)), ('two', dict(x=2))]
        suite = unittest.TestSuite([t])
        suite.scenarios = [('three', dict(y=1)), ('four', dict(y=2))]
        clones = scenarii.multiply_suite(suite)
        # We got the test ones taking over the suite ones
        self.assertTestNames(['test_pass(three)', 'test_pass(four)'], clones)


class TestMultiplyScenarios(unittest.TestCase):

    def test_one_scenario(self):
        scenarios = [('a', dict(b=1))]
        multiplied = scenarii.multiply_scenarios(scenarios)
        # It's a no-op
        self.assertEqual(scenarios, multiplied)

    def test_two_scenarios(self):
        scenarios_a = [('a', dict(x=1))]
        scenarios_b = [('b', dict(y=1, z=1)), ('c', dict(y=2, z=2))]
        multiplied = scenarii.multiply_scenarios(scenarios_a, scenarios_b)
        self.assertEqual([('a,b', dict(x=1, y=1, z=1)),
                          ('a,c', dict(x=1, y=2, z=2))], multiplied)

    def test_three_scenarios(self):
        scenarios_a = [('a', dict(x=1))]
        scenarios_b = [('b1', dict(y=1)), ('b2', dict(y=2))]
        scenarios_c = [('c1', dict(z=1)), ('c2', dict(z=2))]
        multiplied = scenarii.multiply_scenarios(scenarios_a, scenarios_b,
                                                 scenarios_c)
        self.assertEqual([('a,b1,c1', dict(x=1, y=1, z=1)),
                          ('a,b1,c2', {'x': 1, 'y': 1, 'z': 2}),
                          ('a,b2,c1', {'x': 1, 'y': 2, 'z': 1}),
                          ('a,b2,c2', {'x': 1, 'y': 2, 'z': 2})],
                         multiplied)
