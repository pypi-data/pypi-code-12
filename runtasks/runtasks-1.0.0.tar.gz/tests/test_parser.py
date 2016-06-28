
import unittest, logging
from collections import namedtuple

from runtasks import task
from runtasks.tasks import get_task_names
from runtasks.parser import parse, parse_task

logger = logging.getLogger()

@task
def basic(arg1, arg2=False, arg3=True, arg4=None):
    pass

@task
def other(arg1=None, flag=False, forward=False, verbose=False):
    pass

@task(flags={'x': 'flag'})
def flagtest(arg1=None, flag=False, forward=False, verbose=False):
    pass

basicresults    = namedtuple('basicresults', 'arg1 arg2 arg3 arg4')
otherresults    = namedtuple('otherresults', 'arg1 flag forward verbose')
flagtestresults = namedtuple('flagtestresults', 'arg1 flag forward verbose')

class TestParser(unittest.TestCase):

    def test_positional(self):
        "Ensure position parameters work with no dashes"

        # The value "test" should be assigned to arg1 since it has no default.

        cmdline  = 'basic test'
        expected = basicresults(arg1='test', arg2=False, arg3=True, arg4=None)
        args, remaining = parse_task(basic._task, cmdline.split(), other_names=get_task_names())
        self.assertEqual(args.args, expected)
        self.assertFalse(remaining)

    def test_required(self):
        "Fail if not enough values are provided"

        # If we don't provide a value for arg1 it should fail.

        with self.assertRaises(SystemExit):
            cmdline = 'basic'
            parse_task(basic._task, cmdline.split(), other_names=get_task_names())

    def test_reject_bool_vals(self):
        "Fail if a value is provided for a Boolean parameter"

        # arg2 and arg3 both are Booleans, so you can provide "--arg2" or "--no-arg3" but not
        # "--arg2=xyz".

        with self.assertRaises(SystemExit):
            cmdline = 'basic arg2=test'
            parse_task(basic._task, cmdline.split(), other_names=get_task_names())

        with self.assertRaises(SystemExit):
            cmdline = 'basic arg3=test'
            parse_task(basic._task, cmdline.split(), other_names=get_task_names())

    def test_equals(self):
        "test arg=val"
        cmdline  = 'basic test1 arg4=test4'
        expected = basicresults(arg1='test1', arg2=False, arg3=True, arg4='test4')
        args, remaining = parse_task(basic._task, cmdline.split(), other_names=get_task_names())
        self.assertEqual(args.args, expected)
        self.assertFalse(remaining)

    def test_dashes_equals(self):
        "test --arg=val"
        cmdline  = 'basic test1 --arg4=test4'
        expected = basicresults(arg1='test1', arg2=False, arg3=True, arg4='test4')
        args, remaining = parse_task(basic._task, cmdline.split(), other_names=get_task_names())
        self.assertEqual(args.args, expected)
        self.assertFalse(remaining)

    def test_bool(self):
        "test --arg"
        # A parameter with "=False" is a Boolean parameter that can be enabled using the
        # parameter name as a flag: --arg2

        cmdline  = 'basic test1 --arg2'
        expected = basicresults(arg1='test1', arg2=True, arg3=True, arg4=None)
        args, remaining = parse_task(basic._task, cmdline.split(), other_names=get_task_names())
        self.assertEqual(args.args, expected)
        self.assertFalse(remaining)

    def test_bool_no(self):
        "Test --no-arg"
        # A parameter with "=True" is a Boolean parameter that can be disabled by prepending
        # "no-"to the parameter name as a flag: --no-arg3
        cmdline  = 'basic test1 --no-arg3'
        expected = basicresults(arg1='test1', arg2=False, arg3=False, arg4=None)
        args, remaining = parse_task(basic._task, cmdline.split(), other_names=get_task_names())
        self.assertEqual(args.args, expected)
        self.assertFalse(remaining)

    def test_bool_true_flag(self):
        "Test --arg for a default=True"
        # A parameter with "=True" is a Boolean parameter that can be disabled by prepending
        # "no-"to the parameter name as a flag: --no-arg3
        cmdline  = 'basic test1 --arg3'
        expected = basicresults(arg1='test1', arg2=False, arg3=True, arg4=None)
        args, remaining = parse_task(basic._task, cmdline.split(), other_names=get_task_names())
        self.assertEqual(args.args, expected)
        self.assertFalse(remaining)

    def test_bool_false_no(self):
        "Test --no-arg for a default=False"

        # The parameter defaults to False already, but we'll accept --no-arg for readability.
        cmdline  = 'basic test1 --no-arg2'
        expected = basicresults(arg1='test1', arg2=False, arg3=True, arg4=None)
        args, remaining = parse_task(basic._task, cmdline.split(), other_names=get_task_names())
        self.assertEqual(args.args, expected)
        self.assertFalse(remaining)

    def test_remaining(self):
        "Ensure the parser returns the remaining, unrecognized values."
        cmdline = 'basic test1 other'
        expected = basicresults(arg1='test1', arg2=False, arg3=True, arg4=None)
        args, remaining = parse_task(basic._task, cmdline.split(), other_names=get_task_names())
        self.assertEqual(args.args, expected)
        self.assertEqual(remaining, ['other'])

    def test_dont_guess(self):
        "Fail if a token is ambiguous"

        # In this case "other" can either be the value for basic.arg1 or the name of the next
        # task.  Resist the urge to guess.

        with self.assertRaises(SystemExit):
            cmdline = 'basic other'
            parse_task(basic._task, cmdline.split(), other_names=get_task_names())

        # Here's what you'd need to use if you wanted the value "other"
        cmdline  = 'basic arg1=other'
        expected = basicresults(arg1='other', arg2=False, arg3=True, arg4=None)
        args, remaining = parse_task(basic._task, cmdline.split(), other_names=get_task_names())
        self.assertEqual(args.args, expected)
        self.assertFalse(remaining)


class TestShortFlags(unittest.TestCase):
    def test_one_value(self):
        cmdline = 'other -a value1'
        expected = otherresults(arg1='value1', flag=False, forward=False, verbose=False)
        args, remaining = parse_task(other._task, cmdline.split(), other_names=get_task_names())
        self.assertEqual(args.args, expected)
        self.assertFalse(remaining)

    def test_multiple_flags(self):
        cmdline = 'other -va value1'
        expected = otherresults(arg1='value1', flag=False, forward=False, verbose=True)
        args, remaining = parse_task(other._task, cmdline.split(), other_names=get_task_names())
        self.assertEqual(args.args, expected)
        self.assertFalse(remaining)

    def test_flag(self):
        cmdline = 'other -v'
        expected = otherresults(arg1=None, flag=False, forward=False, verbose=True)
        args, remaining = parse_task(other._task, cmdline.split(), other_names=get_task_names())
        self.assertEqual(args.args, expected)
        self.assertFalse(remaining)

    def test_multiple_matches(self):
        "There can only be one parameter per letter"

        # The "other" task has two parameters that start with 'f', so 'f' is not a valid flag.

        with self.assertRaises(SystemExit):
            cmdline = 'other -f'
            parse_task(other._task, cmdline.split(), other_names=get_task_names())

    def test_manual_flags(self):
        # The flagtest task has a flag set specifically by the user.
        cmdline = 'flagtest -vx'
        expected = flagtestresults(arg1=None, flag=True, forward=False, verbose=True)
        args, remaining = parse_task(flagtest._task, cmdline.split(), other_names=get_task_names())
        self.assertEqual(args.args, expected)
        self.assertFalse(remaining)

    def test_manual_flags_multiple(self):
        # The flagtest task has two arguments that start with "f", but we've assigned "x" to
        # one of them.  That means "f" should work for the other.
        cmdline = 'flagtest -f'
        expected = flagtestresults(arg1=None, flag=False, forward=True, verbose=False)
        args, remaining = parse_task(flagtest._task, cmdline.split(), other_names=get_task_names())
        self.assertEqual(args.args, expected)
        self.assertFalse(remaining)
