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

import argparse
import sys


import testtools


from olstests import (
    filters,
    loaders,
    results,
    suites,
)


class PickAction(argparse.Action):
    """Implements --pick error checking and conversion.

    For a 'n/m' valid string the value will be [n, m].
    """

    def __call__(self, parser, namespace, values, option_string=None):
        value = values  # There is only one

        def BadValue(msg):
            return argparse.ArgumentError(self, msg)

        try:
            rank, modulo = value.split('/')
        except ValueError:
            raise BadValue('{} does not match n/m format'.format(value))

        def check_int(val):
            try:
                return abs(int(val))
            except ValueError:
                raise BadValue('{} is not an integer'.format(val))

        rank, modulo = [check_int(rank), check_int(modulo)]
        if not rank or not modulo:
            raise BadValue('Zero makes no sense in {}'.format(value))
        if rank > modulo:
            raise BadValue(
                '{} must be <= {} in {}'.format(rank, modulo, value))
        setattr(namespace, self.dest, [rank, modulo])


def add_ols_run_tests_options(parser, positional=False):
    if positional:
        args = ('include_regexps',)
        kwargs = dict(nargs='*')
    else:
        args = ('--include', '-i')
        kwargs = dict(action='append', dest='include_regexps',
                      default=None)
    parser.add_argument(
        *args, metavar='INCLUDE',
        help='All tests matching the INCLUDE regexp will be run.'
        ' Can be repeated.', **kwargs)
    # Optional arguments
    parser.add_argument(
        '--module', '-m', metavar='MODULE', action='append',
        dest='modules',
        help='Load tests from MODULE[:PATH]. MODULE is found in'
        ' python path or PATH if specified.'
        ' Can be repeated.')
    parser.add_argument(
        '--exclude', '-X', metavar='EXCLUDE', action='append',
        dest='exclude_regexps',
        help='All tests matching the EXCLUDE regexp will not be run.'
        ' Can be repeated.')
    parser.add_argument(
        '--list', '-l', action='store_true',
        dest='list_only',
        help='List the tests instead of running them.')
    parser.add_argument(
        '--load', action='store', type=argparse.FileType('r'),
        dest='load_file',
        help='A file name containing test ids to be run'
        ' in the specified order.')
    parser.add_argument(
        '--format', '-f', choices=['text', 'subunit'], default='text',
        help='Output format for the test results.')
    parser.add_argument(
        '--concurrency', '-c', dest='concurrency',
        default=1, type=int,
        help='concurrency (number of processes).')
    parser.add_argument(
        '--pick', dest='pick',
        default=None, action=PickAction,
        help='n/m pick nth test every m tests.')


class RunTestsArgParser(argparse.ArgumentParser):
    """A parser for the ols-run-tests script.

    This can be used as a base class for scripts that want to add more options
    to suit their needs.
    """

    def __init__(self, prog=None, description=None):
        if prog is None:
            prog = 'ols-run-tests'
        if description is None:
            description = 'Load and run tests.'
        super(RunTestsArgParser, self).__init__(prog=prog,
                                                description=description)
        add_ols_run_tests_options(self, positional=True)

    def parse_args(self, args=None, out=None, err=None):
        """Parse arguments, overridding stdout/stderr if provided.

        Overridding stdout/stderr is provided for tests.

        :params args: The arguments to the script.

        :param out: Default to sys.stdout.

        :param err: Default to sys.stderr.

        :return: The populated namespace.
        """
        out_orig = sys.stdout
        err_orig = sys.stderr
        try:
            if out is not None:
                sys.stdout = out
            if err is not None:
                sys.stderr = err
            return super(RunTestsArgParser, self).parse_args(args)
        finally:
            sys.stdout = out_orig
            sys.stderr = err_orig


def cli_run(args=None, stdout=None, stderr=None):
    """Run tests from the command line."""
    if args is None:
        args = sys.argv[1:]
    if stdout is None:
        stdout = sys.stdout
    if stderr is None:
        stderr = sys.stderr
    parser = RunTestsArgParser()
    ns = parser.parse_args(args)
    suite = load_tests(ns.include_regexps, ns.exclude_regexps,
                       modules=ns.modules, load_list_file=ns.load_file,
                       pick=ns.pick)
    if ns.list_only:
        ret = list_tests(suite, stdout)
    else:
        if ns.format == 'text':
            result = results.TextResult(stdout, verbosity=2)
        else:
            result = results.SubunitProducer(stdout)
        ret = run_tests(suite, result, ns.concurrency)
    return ret


def load_tests(include_regexps, exclude_regexps=None,
               modules=None, load_list_file=None, pick=None):
    """Load tests matching inclusive and exclusive regexps.

    :param include_regexps: A list of regexps describing the tests to include.

    :param exclude_regexps: A list of regexps describing the tests to exclude.

    :param modules: A list of module python names from which the tests should
        be loaded. Default to None which fallbacks to loading tests from the
        current directory.

    :param load_list_file: A file handle containing a list of test ids, one by
        line.

    :param pick: An optional (rank, modulo) tuple to pick a subset of the
        suite.

    :return: The test suite for all collected tests.
    """
    loader = loaders.Loader()
    suite = loader.suiteClass()
    if modules is None:
        suite.addTests(loader.loadTestsFromTree('.'))
    else:
        for mod_name in modules:
            mod_tests = loader.loadTestsFromSysPathModule(mod_name)
            if mod_tests is not None:
                suite.addTests(mod_tests)
    suite = filters.include_regexps(include_regexps, suite)
    suite = filters.exclude_regexps(exclude_regexps, suite)
    if load_list_file is not None:
        id_list = filters.load_test_id_list(load_list_file)
        suite = filters.include_id_list(id_list, suite)
    if pick is not None:
        rank, modulo = pick
        suite = filters.pick(suite, rank, modulo)
    return suite


def list_tests(suite, stream):
    """List the test ids , one by line.

    :param suite: A test suite to list.

    :param stream: A writable stream.

    :return: 0 on success, 1 otherwise.

    :note: Listing no tests is an error. The rationale is that when used from a
        script, most people expects to select at least one test and there has
        been numerous reports of people being confused that listing *no* tests
        wasn't flagged as an error. In most of these cases, *another* error led
        to no tests being selected but trapping it here helps.
    """
    no_tests = True
    for t in filters.iter_flat(suite):
        stream.write('{}\n'.format(t.id()))
        no_tests = False
    return int(no_tests)


def run_tests(suite, result, process_nb=1, split_suite=suites.ForkedSuite):
    """Run the provided tests with the provided test result.

    :param suite: A test suite.

    :param result: The collecting test result object.

    :param process_nb: The number of processes to split the run across.

    :param split_suite: The suite class to use for the splitted suite when
        ``nb_process`` is greater than 1.

    :return: 0 on success, 1 otherwise.

    :note: Running no tests is an error. The rationale is that when used from a
        script, most people expects to run at least one test and there has been
        numerous reports of people being confused that running *no* tests
        wasn't flagged as an error. In most of these cases, *another* error led
        to no tests being run but trapping it here helps.

    """
    if process_nb <= 1:
        result.startTestRun()
        try:
            suite.run(result)
        finally:
            result.stopTestRun()
    else:
        # Split the tests for workers
        def split_tests():
            for unique, sub_suite in enumerate(
                    filters.partition_suite(suite, process_nb), start=1):
                yield split_suite(sub_suite, unique, process_nb), unique
        # Wrap the result so it can receive a testtools stream and forward the
        # events to the received ``result``.
        conc_res = testtools.StreamToExtendedDecorator(result)
        conc_res.startTestRun()
        try:
            conc = testtools.ConcurrentStreamTestSuite(split_tests)
            conc.run(conc_res)
        finally:
            conc_res.stopTestRun()
    return int(not (result.wasSuccessful() and result.testsRun > 0))
