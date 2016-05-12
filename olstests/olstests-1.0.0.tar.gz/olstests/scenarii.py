# This file is part of the Online Services test tools
#
# Copyright 2014, 2015 Canonical Ltd.
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
"""Test scenarios handling.

This provides support for parametrized tests through the definition of a test
class attribute called scenarios describing which test objects should be
created.

A scenario is defined by a name and a dict.

The name is used to uniquely identify a test object by adding it to the test
id().

The dict defines a set of test object attributes that will be set to the
corresponding values.

The unusual (but etymologically correct) plural form of scenario is used for
the module name to avoid colliding with 'scenarios' that users are encouraged
to use for scenarios definitions.

"""

import copy
import functools
import unittest


def clone_test(test, new_id):
    """Clone a test giving it a new id.

    This should only be used on test objects that have just been created but
    not executed.

    :param test: The test to clone.

    :param new_id: The id to assign to it.

    :return: The cloned test.

    """
    clone = copy.copy(test)
    clone.id = lambda: new_id
    return clone


def apply_scenario(test, scenario):
    """Copy a test and apply a scenario.

    :param test: The test receiving the scenario

    :param scenario: A tuple describing the scenario.
        The first element of the tuple is the new test id.
        The second element is a dict containing attributes to set on the
        test.
    :return: The adapted test.
    """
    name, attrs = scenario
    # Adding the name between parens preserve unique ids
    new_id = '{}({})'.format(test.id(), name)
    new_test = clone_test(test, new_id)
    for name, value in attrs.items():
        setattr(new_test, name, value)
    return new_test


def apply_scenarios(test, scenarios):
    """Apply the scenarios to test and yield the cloned tests.

    :param test: The test to apply scenarios to.

    :param scenarios: An iterable of scenarios to apply to the test.
    """
    for scenario in scenarios:
        yield apply_scenario(test, scenario)


def multiply_suite(suite, scenarios=None):
    """Multiply suite by scenarios.

    :param suite: The suite to parameterize. It contains either tests or suites
        inheriting from ``unittest.TestSuite``.

    :param scenarios: The scenarios to apply. If None is supplied (the
        default), the test 'scenarios' attributes will be used when
        encountered.

    :returns: The parametrized test suite.

    ``suite`` is a tree of tests and suites, the returned suite respect the
    received suite layout.

    """
    multiplied_suite = suite.__class__()
    suite_scenarios = getattr(suite, 'scenarios', None)
    if scenarios is None and suite_scenarios is not None:
        # We use the scenarios from the suite from now on.
        scenarios = suite_scenarios
    for test in suite:
        if issubclass(test.__class__, unittest.TestSuite):
            # We received a suite, we multiply that suite
            multiplied = multiply_suite(test, scenarios)
        else:
            test_scenarios = getattr(test, 'scenarios', None)
            if scenarios is None and test_scenarios is not None:
                # We use the scenarios from the suite from now on.
                scenarios = test_scenarios
            if scenarios is None:
                # No scenarios so the test is left untouched
                multiplied = [test]
            else:
                # Now we multiply, for real
                multiplied = list(apply_scenarios(test, scenarios))
        multiplied_suite.addTests(multiplied)
    return multiplied_suite


def load_tests_with_scenarios(loader, module_tests, pattern):
    """Multiply tests depending on their 'scenarios' attribute.

    This is a shorcut that can be assigned to 'load_tests' in any test module
    to make this automatically work across tests in the module (whether they
    specify a 'scenarios' attribute or not).
    """
    return multiply_suite(module_tests)


def multiply_scenarios(*scenarios):
    """Multiply two or more iterables of scenarios.

    :returns: A list of compound scenarios: the cross-product of all scenarios,
        with the names concatenated and the parameter dicts merged together.

    """

    def multiply(these_scenarios, those_scenarios):
        """Multiply two sets of scenarios.

        :returns: the cartesian product of the two sets of scenarios.
        """
        return [('{},{}'.format(this_name, that_name),
                 dict(list(this_dict.items()) + list(that_dict.items())))
                for this_name, this_dict in these_scenarios
                for that_name, that_dict in those_scenarios]

    return functools.reduce(multiply, map(list, scenarios))
