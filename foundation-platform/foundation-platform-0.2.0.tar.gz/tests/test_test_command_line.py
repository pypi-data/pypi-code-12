from contextlib import contextmanager
import foundation_platform.command_line as command_line
from io import StringIO
import sys
import unittest2 as unittest


# Capture output from stdout and stderr (so that it doesn't clutter up the test output with
# useless information)
@contextmanager
def capture_sys_output():
    capture_out, capture_err = StringIO(), StringIO()
    current_out, current_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = capture_out, capture_err
        yield capture_out, capture_err
    finally:
        sys.stdout, sys.stderr = current_out, current_err


class TestCommandLine(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestCommandLine, self).__init__(*args, **kwargs)
        self.__parser = None

    def setUp(self):
        self.__parser = command_line.CsarParser()

    # The following tests verify the basic sanity of command line parsing.  We don't care about
    # the exact output provided, but each case should have an exit code of 0, meaning that we
    # successfully created a parser which accepts the expected commands.
    #
    def test_help(self):
        # Passes if --help returns successfully - don't care about the exact output
        with self.assertRaises(SystemExit) as cm:
            with capture_sys_output() as (stdout, stderr):
                self.__parser.parse("--help")
        self.assertEqual(cm.exception.code, 0, "help command failed -" +
                         " stdout=" + stdout.getvalue() + " stderr=" + stderr.getvalue())

    def test_version(self):
        # Passes if --version returns successfully - don't care about the exact output
        with self.assertRaises(SystemExit) as cm:
            with capture_sys_output() as (stdout, stderr):
                self.__parser.parse("--version")
        self.assertEqual(cm.exception.code, 0, "version command failed -" +
                         " stdout=" + stdout.getvalue() + " stderr=" + stderr.getvalue())

    def test_create_help(self):
        # Passes if we can get help for the create command
        with self.assertRaises(SystemExit) as cm:
            with capture_sys_output() as (stdout, stderr):
                self.__parser.parse("create --help")
        self.assertEqual(cm.exception.code, 0, "create command help failed -" +
                         " stdout=" + stdout.getvalue() + " stderr=" + stderr.getvalue())

    def test_load_file_help(self):
        # Passes if we can get help for the load_file command
        with self.assertRaises(SystemExit) as cm:
            with capture_sys_output() as (stdout, stderr):
                self.__parser.parse("load_file --help")
        self.assertEqual(cm.exception.code, 0, "load_file command help failed -" +
                         " stdout=" + stdout.getvalue() + " stderr=" + stderr.getvalue())

    def test_load_url_help(self):
        # Passes if we can get help for the load_url command
        with self.assertRaises(SystemExit) as cm:
            with capture_sys_output() as (stdout, stderr):
                self.__parser.parse("load_url --help")
        self.assertEqual(cm.exception.code, 0, "load_url command help failed -" +
                         " stdout=" + stdout.getvalue() + " stderr=" + stderr.getvalue())


def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCommandLine)
    suite()

if __name__ == '__main__':
    main()
