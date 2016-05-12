# This file is part of the Online Services test tools
#
# Copyright 2013-2016 Canonical Ltd.
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
"""Filter tests suite with regular expressions."""

import re
import unittest


def filter_suite(condition, suite):
    """Return tests for which ``condition`` is True in ``suite``.

    :param condition: A callable receiving a test and returning True if the
        test should be kept.

    :param suite: A test suite that can be iterated. It contains either tests
        or a suite inheriting from ``unittest.TestSuite``.

    ``suite`` is a tree of tests and suites, the returned suite respect the
    received suite layout, only removing empty suites.
    """
    filtered_suite = suite.__class__()
    for test in suite:
        if issubclass(test.__class__, unittest.TestSuite):
            # We received a suite, we'll filter a suite
            filtered = filter_suite(condition, test)
            if filtered.countTestCases():
                # Keep only non-empty suites
                filtered_suite.addTest(filtered)
        elif condition(test):
            # The test is kept
            filtered_suite.addTest(test)
    return filtered_suite


def pick(suite, rank, modulo):
    """Pick some tests in ``suite```.

    :param suite: The suite to pick tests from.

    :param rank: The test to pick every ``modulo`` tests when iterating
        ``suite``.

    :param modulo: How often is ``rank`` picked.

    :returns: A suite of tests picking the ``rank``nth test every ``modulo``
        tests from ``suite``.

    """
    if not modulo:
        # modulo == zero is a special case, we keep all tests
        return suite
    # global but declared inside the func so the inner 'nth' func can modify it
    global __nth_calls
    __nth_calls = 0

    def nth(test):
        global __nth_calls
        try:
            if __nth_calls + 1 == rank:
                return True
        finally:
            __nth_calls = (__nth_calls + 1) % modulo
        return False
    return filter_suite(nth, suite)


def partition_suite(suite, count):
    """Partition suite into ``count`` suites.

    :param suite: The suite to partition.

    :param count: The number of suites to build.

    :returns: A list of ``count`` suites respecting the ``suite`` layout,
        dropping inner empty suites.
    """
    # This just assigns tests in a round-robin fashion.  On one hand this
    # splits up blocks of related tests that might run faster if they share
    # resources, but on the other it avoids assigning blocks of slow tests to
    # just one partition.  So the slowest partition shouldn't be much slower
    # than the fastest (confirmed IRL, not a metric, etc ;).
    global __nth_calls  # global but declared inside the func
    suites = []
    for cur in range(count):
        __nth_calls = 0

        def nth(test):
            """Returns True for the 'cur'th suite.

            This just counts the calls and check ``cur``.
            """
            global __nth_calls
            try:
                if __nth_calls == cur:
                    return True
            finally:
                __nth_calls = (__nth_calls + 1) % count
            return False

        # Each suite is built taking each nth test, relying on filter_suite to
        # preserve the layout.
        suites.append(filter_suite(nth, suite))
    return suites


def iter_flat(this):
    """Iterate a suite or yield a test.

    When preserving the test suite shape (a tree in the general case) is not a
    concern, this is the easiest way to iterate a test suite.
    """
    try:
        suite = iter(this)
    except TypeError:
        # If it can't be iterated, it's a test
        yield this
    else:
        for that in suite:
            for t in iter_flat(that):
                yield t


def include_regexps(regexps, suite):
    """Returns the tests that match one of ``regexps``.

    :param regexps: A list of test id regexps (strings, will be compiled
        internally) to include. All tests are included if no regexps are
        provided.

    :param suite: The test suite to filter.
    """
    if not regexps:
        # No regexeps, no filtering
        return suite

    def matches_one_of(test):
        # A test is kept if its id matches one of the regexps
        tid = test.id()
        for reg in regexps:
            if re.search(reg, tid) is not None:
                return True
        return False
    return filter_suite(matches_one_of, suite)


def exclude_regexps(regexps, suite):
    """Returns the tests whose id does not match with any of the regexps.

    :param regexps: A list of test id regexps (strings, will be compiled
        internally) to exclude. No tests are excluded if no regexps are
        provided.

    :param suite: The test suite to filter.
    """
    if not regexps:
        # No regexeps, no filtering
        return suite

    def matches_none_of(test):
        # A test is kept if its id matches none of the regexps
        tid = test.id()
        for regexp in regexps:
            if re.search(regexp, tid):
                return False
        return True
    return filter_suite(matches_none_of, suite)


def load_test_id_list(file_handle):
    """Load a test id list from a file handle.

    The format is one test id by line.  No special care is taken to impose
    strict rules, these test ids are used to filter the test suite so a test id
    that do not match an existing test will do no harm. This allows user to add
    comments, leave blank lines, etc as they won't match existing test ids.

    On the flip side, this means no control can be made about typos (a
    non-matching test id won't be run) but in practice, the test ids are copied
    from a previous run so typos are unlikely.
    """
    test_list = []
    for test_name in file_handle.readlines():
        test_list.append(test_name.strip())
    return test_list


def include_id_list(id_list, suite):
    """Returns the tests whose id are part of the list.

    The order in the list is enforced in the returned suite. This provides a
    way to strictly control the order of execution, making isolation issues
    easier to diagnose.

    Note that this doesn't filter out duplicates in the list, instead, such
    duplicates are provided twice.

    :param id_list: A list of test ids that should be kept.

    :param suite: The test suite to filter.

    """
    if not id_list:
        # No ids, no tests
        return suite.__class__()

    filtered = suite.__class__()
    for the_id in id_list:

        def is_the_id(test):
            return test.id() == the_id
        just_the_id = filter_suite(is_the_id, suite)
        # We don't want to wrap the filtered tests into two layers of
        # suite.__class__ so we extract the single test.
        if just_the_id.countTestCases():
            # Keep only non-empty suites
            filtered.addTest(list(just_the_id)[0])
    return filtered
