# Copyright 2016 Louis Paternault
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Tests"""

import contextlib
import os
import re
import sys
import tempfile
import unittest

from .redirector import redirect_stdout

import argdispatch

class SuppressStandard:
    """A context manager suppressing standard output and error

    Adapted from an original work:
    By jeremiahbuddha https://stackoverflow.com/users/772487/jeremiahbuddha
    Copied from http://stackoverflow.com/q/11130156
    Licensed under CC by-sa 3.0.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, output=True, error=True):
        # Open a pair of null files
        self.null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
        # Save the actual stdout (1) and stderr (2) file descriptors.
        self.save_fds = (os.dup(1), os.dup(2))

        self.output = output
        self.error = error

    def __enter__(self):
        # Assign the null pointers to stdout and stderr.
        if self.output:
            os.dup2(self.null_fds[0], 1)
        if self.error:
            os.dup2(self.null_fds[1], 2)

    def __exit__(self, *_):
        # Re-assign the real stdout/stderr back to (1) and (2)
        if self.output:
            os.dup2(self.save_fds[0], 1)
        if self.error:
            os.dup2(self.save_fds[1], 2)
        # Close the null files
        os.close(self.null_fds[0])
        os.close(self.null_fds[1])

def function_foo(args):
    """This is the docstring of function foo."""
    print("Running function_foo({})".format(", ".join(args)))
    sys.exit(1)

def function_bar(args):
    """This is the docstring of function bar."""
    print("Running function_bar({})".format(", ".join(args)))
    return 1

def function_none(args):
    """This is the docstring of function none."""
    print("Running function_none({})".format(", ".join(args)))

def function_nodocstring(args):
    # pylint: disable=missing-docstring, unused-argument
    pass

def function_emptydocstring(args):
    # pylint: disable=trailing-whitespace, unused-argument, empty-docstring
    """
       
    """
    pass

def testdatapath(*paths):
    """Return the given path, relative to the test data directory."""
    return os.path.join(os.path.dirname(__file__), "data", *paths)

class pythonpath(contextlib.ContextDecorator):
    """Decorator to extend ``sys.path``."""
    # pylint: disable=invalid-name, too-few-public-methods

    def __init__(self, *path):
        self.path = path

    def __enter__(self):
        sys.path = [
            testdatapath(path)
            for path in self.path
            ] + sys.path
        return self

    def __exit__(self, *exc):
        sys.path = sys.path[len(self.path):]
        return False

class binpath(contextlib.ContextDecorator):
    """Decorator to replace ``PATH`` argument variable."""
    # pylint: disable=invalid-name, too-few-public-methods

    def __init__(self, *path):
        self.path = path

    def __enter__(self):
        # pylint: disable=attribute-defined-outside-init
        # Making the python executable callable
        self.pythondir = tempfile.TemporaryDirectory()
        os.symlink(sys.executable, os.path.join(self.pythondir.name, "python"))
        # Setting path
        self.oldpath = os.environ.get('PATH')
        os.environ['PATH'] = ":".join(
            [self.pythondir.name]
            +
            [
                testdatapath(path)
                for path in self.path
            ])
        return self

    def __exit__(self, *exc):
        os.environ['PATH'] = self.oldpath
        self.pythondir.cleanup()
        return False

class TestArgparse(unittest.TestCase):
    """Generic test class, defining some utilities."""

    @staticmethod
    def _ArgumentParser():
        """Return an `ArgumentParser` object."""
        # pylint: disable=invalid-name
        return argdispatch.ArgumentParser(prog=sys.executable)

    @contextlib.contextmanager
    def assertExit(self, code=None):
        """Assert that code calls :func:`sys.exit`.

        :param code: If not ``None``, fails if exit code is different from this argument.
        """
        # pylint: disable=invalid-name
        with self.assertRaises(SystemExit) as context:
            yield
        if code is None:
            return
        self.assertEqual(code, context.exception.code)

    @contextlib.contextmanager
    def assertStdoutMatches(self, pattern, *, count=None):
        """Assert that standard output matches the given pattern.

        :param int count: If not ``None``, fails if number of matches is
            different from this argument.
        """
        # pylint: disable=invalid-name
        with tempfile.NamedTemporaryFile() as writefile:
            with redirect_stdout(writefile.name):
                yield
            with open(writefile.name) as readfile:
                stdout = "".join(readfile.readlines())
        found = re.findall(pattern, stdout, flags=re.MULTILINE)
        if count is None:
            if not found:
                raise AssertionError("Pattern '{}' not found in '{}'.".format(pattern, stdout))
        else:
            self.assertEqual(len(found), count)


class TestParse(TestArgparse):
    """Test that subparsers definition, and method `parse_args`."""

    def test_add_parser(self):
        """Test the legacy `add_parser` method."""
        parser = argdispatch.ArgumentParser()
        sub = parser.add_subparsers()
        parser_foo = sub.add_parser("foo")
        parser_foo.set_defaults(sub="foo")
        parser_bar = sub.add_parser("bar")
        parser_bar.set_defaults(sub="bar")
        with self.subTest():
            self.assertEqual(parser.parse_args("foo".split()).sub, "foo")
        with self.subTest():
            self.assertEqual(parser.parse_args("bar".split()).sub, "bar")
        with self.subTest():
            with SuppressStandard():
                with self.assertExit(2):
                    parser.parse_args("baz".split())

    def test_several_subparsers(self):
        """Test what happens when several subparsers are defined."""
        with SuppressStandard():
            parser = argdispatch.ArgumentParser()
            parser.add_subparsers()
            with self.assertExit(2):
                parser.add_subparsers()

    @binpath("binpath1", "binpath2")
    def test_executable(self):
        """Test the `add_executable` method."""
        parser = argdispatch.ArgumentParser()
        sub = parser.add_subparsers()
        sub.add_executable("bin11")
        sub.add_executable("bin12", "foo")
        with self.subTest():
            with self.assertStdoutMatches(r"^Running .*bin11$"):
                with self.assertExit(0):
                    parser.parse_args("bin11".split())
        with self.subTest():
            with self.assertStdoutMatches(r"^Running .*bin11 --some arguments$"):
                with self.assertExit(0):
                    parser.parse_args("bin11 --some arguments".split())
        with self.subTest():
            with self.assertStdoutMatches(r"^Running .*bin12 bar baz$"):
                with self.assertExit(0):
                    parser.parse_args("foo bar baz".split())

    @binpath("binpath1", "binpath2")
    def test_pattern_executables(self):
        """Test the `add_pattern_executables` method."""
        parser = argdispatch.ArgumentParser()
        sub = parser.add_subparsers()
        sub.add_pattern_executables(".*2$")
        with self.subTest():
            with self.assertStdoutMatches(r"^Running .*bin12$"):
                with self.assertExit(0):
                    parser.parse_args("bin12".split())
        with self.subTest():
            with self.assertStdoutMatches(r"^Running .*bin22$"):
                with self.assertExit(0):
                    parser.parse_args("bin22".split())
        with self.subTest():
            with SuppressStandard():
                with self.assertExit(2):
                    parser.parse_args("bin11".split())

    @binpath("binpath1", "binpath2")
    def test_pattern_named_group(self):
        """Test the `add_pattern_executables` method, with a named group."""
        parser = argdispatch.ArgumentParser()
        sub = parser.add_subparsers()
        sub.add_pattern_executables("^(?P<command>.*)2$")
        with self.subTest():
            with self.assertStdoutMatches(r"^Running .*bin12$"):
                with self.assertExit(0):
                    parser.parse_args("bin1".split())
        with self.subTest():
            with self.assertStdoutMatches(r"^Running .*bin22$"):
                with self.assertExit(0):
                    parser.parse_args("bin2".split())
        with self.subTest():
            with SuppressStandard():
                with self.assertExit(2):
                    parser.parse_args("bin12".split())

    @binpath("binpath1", "binpath2")
    def test_prefix_executables(self):
        """Test the `add_prefix_executables` method."""
        parser = argdispatch.ArgumentParser()
        sub = parser.add_subparsers()
        sub.add_prefix_executables("bin1")
        with self.subTest():
            with self.assertStdoutMatches(r"^Running .*bin11$"):
                with self.assertExit(0):
                    parser.parse_args("1".split())
        with self.subTest():
            with self.assertStdoutMatches(r"^Running .*bin12$"):
                with self.assertExit(0):
                    parser.parse_args("2".split())
        with self.subTest():
            with SuppressStandard():
                with self.assertExit(2):
                    parser.parse_args("bin11".split())

    def test_function(self):
        """Test the `add_function` method."""
        parser = argdispatch.ArgumentParser()
        sub = parser.add_subparsers()
        sub.add_function(function_foo)
        sub.add_function(function_bar, "bar")
        sub.add_function(function_foo, "foo")
        with self.subTest():
            with self.assertStdoutMatches(r"^Running function_foo\(arg\)$"):
                with self.assertExit(1):
                    parser.parse_args("foo arg".split())
        with self.subTest():
            with self.assertStdoutMatches(r"^Running function_bar\(arg\)$"):
                with self.assertExit(1):
                    parser.parse_args("bar arg".split())
        with self.subTest():
            with self.assertStdoutMatches(r"^Running function_foo\(arg\)$"):
                with self.assertExit(1):
                    parser.parse_args("function_foo arg".split())

    def test_function_return_none(self):
        """Test the `add_function` method, with a function returning ``None``."""
        parser = argdispatch.ArgumentParser()
        sub = parser.add_subparsers()
        sub.add_function(function_none, "none")
        with self.assertStdoutMatches(r"^Running function_none\(--some, arguments\)$"):
            with self.assertExit(None):
                parser.parse_args("none --some arguments".split())

    @pythonpath("pythonpath1", "pythonpath2.zip")
    def test_module(self):
        """Test the `add_module` method."""
        parser = argdispatch.ArgumentParser()
        sub = parser.add_subparsers()
        sub.add_module("foo")
        sub.add_module("foo.bar", "bar")
        sub.add_module("zipfoo")
        sub.add_module("zipfoo.zipbar", "zipbar")
        with self.subTest():
            with self.assertStdoutMatches(r"^Running python module foo.__main__\s*$"):
                with self.assertExit(0):
                    parser.parse_args("foo".split())
            with self.assertStdoutMatches(r"^Running python module foo.bar.__main__\s*$"):
                with self.assertExit(0):
                    parser.parse_args("bar".split())
        with self.subTest():
            with self.assertStdoutMatches(r"^Running python module zipfoo.__main__\s*$"):
                with self.assertExit(0):
                    parser.parse_args("zipfoo".split())
            with self.assertStdoutMatches(r"^Running python module zipfoo.zipbar.__main__\s*$"):
                with self.assertExit(0):
                    parser.parse_args("zipbar".split())

    @pythonpath("pythonpath1", "pythonpath2.zip")
    def test_add_submodules(self):
        """Test the `add_submodules` method."""
        parser = argdispatch.ArgumentParser()
        sub = parser.add_subparsers()
        sub.add_submodules("foo")
        sub.add_submodules("zipfoo")
        sub.add_submodules("???doesnotexist???")
        with self.subTest():
            with self.assertStdoutMatches(r"^Running python module foo.bar.__main__\s*$"):
                with self.assertExit(0):
                    parser.parse_args("bar".split())
        with self.subTest():
            with self.assertStdoutMatches(r"^Running python module zipfoo.zipbar.__main__\s*$"):
                with self.assertExit(0):
                    parser.parse_args("zipbar".split())

class TestErrors(TestArgparse):
    """Test various errors."""

    @binpath("doesnotexist")
    def test_non_existent_path(self):
        """Test the `add_prefix_executables` method, with a non-existent path."""
        # pylint: disable=no-self-use
        parser = argdispatch.ArgumentParser()
        sub = parser.add_subparsers()

        # Nothing special to test here, excepted that this should not raise any Exception.
        sub.add_prefix_executables("bin")

    @binpath("binpath1", "binpath1")
    def test_double_path(self):
        """Test the `add_prefix_executables` method, with a path appearing twice."""
        parser = argdispatch.ArgumentParser()
        sub = parser.add_subparsers()
        sub.add_prefix_executables("bin")

        with self.assertStdoutMatches(r"^\s*11\s*", count=1):
            with self.assertExit(0):
                parser.parse_args("--help".split())

    @pythonpath("pythonpath1", "pythonpath2.zip")
    def test_module(self):
        """Test the `add_module` method, with modules that cannot be imported."""
        parser = argdispatch.ArgumentParser()
        sub = parser.add_subparsers()
        with self.subTest():
            with self.assertRaises(ImportError):
                sub.add_module("???doesnotexist???")
        with self.subTest():
            with self.assertRaises(ImportError):
                sub.add_module("importerror")

    def test_relative_module(self):
        """Test the `add_submodules` method, with relative modules."""
        parser = argdispatch.ArgumentParser()
        sub = parser.add_subparsers()
        with self.assertRaises(NotImplementedError):
            sub.add_submodules(".foo")

    @pythonpath("pythonpath1", "pythonpath2.zip")
    def test_add_submodules(self):
        """Test the `add_submodules` method."""
        parser = argdispatch.ArgumentParser()
        sub = parser.add_subparsers()
        with self.subTest():
            sub.add_submodules("foo", onerror=argdispatch.IGNORE)
        with self.subTest():
            with self.assertRaises(ImportError):
                sub.add_submodules("foo", onerror=argdispatch.RAISE)

    def test_nocommand(self):
        """Test what happens when no subcommand is given."""
        parser = argdispatch.ArgumentParser()
        sub = parser.add_subparsers()
        sub.add_module("foo")

        self.assertIsInstance(parser.parse_args("".split()), argdispatch.Namespace)

        sub.required = True
        sub.dest = "subcommand"
        with SuppressStandard():
            with self.assertExit(2):
                parser.parse_args("".split())

class TestPath(TestArgparse):
    """Test the ``path`` argument."""

    def test_add_executable(self):
        """Test with executables that do not exist."""
        parser = argdispatch.ArgumentParser()
        sub = parser.add_subparsers()
        with self.subTest():
            # Nothing should fail, although executable `bin21` does not exists in path
            sub.add_executable("bin21")
        with self.subTest():
            with self.assertRaises(FileNotFoundError):
                parser.parse_args("bin21".split())

    def test_add_prefix_executables(self):
        """Test various errors with the ``add_prefix_executables`` method."""
        parser = argdispatch.ArgumentParser()
        sub = parser.add_subparsers()
        sub.add_prefix_executables("bin", path=[testdatapath("binpath1")])
        with self.subTest():
            with self.assertStdoutMatches(r"^Running .*bin11$"):
                with self.assertExit(0):
                    parser.parse_args("11".split())
        with self.subTest():
            with SuppressStandard():
                with self.assertExit(2):
                    parser.parse_args("21".split())

    def test_add_module(self):
        """Test various errors with the ``add_module`` method."""
        parser = argdispatch.ArgumentParser()
        sub = parser.add_subparsers()
        sub.add_module("foo", path=[testdatapath("pythonpath1")])
        with self.subTest():
            with self.assertStdoutMatches(r"^Running python module foo.__main__\s*$"):
                with self.assertExit(0):
                    parser.parse_args("foo".split())
        with self.subTest():
            with SuppressStandard():
                with self.assertExit(2):
                    parser.parse_args("zipbar".split())

    def test_add_submodules(self):
        """Test various errors with the ``add_submodules`` method."""
        parser = argdispatch.ArgumentParser()
        sub = parser.add_subparsers()
        sub.add_submodules("foo", path=[testdatapath("pythonpath1")])
        with self.subTest():
            with self.assertStdoutMatches(r"^Running python module foo.bar.__main__\s*$"):
                with self.assertExit(0):
                    parser.parse_args("bar".split())
        with self.subTest():
            with SuppressStandard():
                with self.assertExit(2):
                    parser.parse_args("zipbar".split())

    @pythonpath("pythonpath3")
    def test_module_or_package(self):
        """Test various errors related to modules and packages."""
        parser = argdispatch.ArgumentParser()
        sub = parser.add_subparsers()
        with self.subTest():
            with self.assertRaises(ImportError):
                sub.add_module("empty")
        with self.subTest():
            with self.assertRaises(ImportError):
                sub.add_module("withinit")
        with self.subTest():
            with self.assertRaises(ImportError):
                sub.add_module("withoutinit")
        sub.add_module("isamodule")
        sub.add_module("withinit.foo")
        sub.add_module("withmain")
        with self.subTest():
            with self.assertStdoutMatches(r"^Running python module isamodule\s*$"):
                with self.assertExit(0):
                    parser.parse_args("isamodule".split())
        with self.subTest():
            with self.assertStdoutMatches(r"^Running python module withinit.foo\s*$"):
                with self.assertExit(0):
                    parser.parse_args("withinit.foo".split())
        with self.subTest():
            with self.assertStdoutMatches(r"^Running python module withmain.__main__\s*$"):
                with self.assertExit(0):
                    parser.parse_args("withmain".split())


class TestOndouble(TestArgparse):
    """Test of the ``ondouble`` argument."""

    @pythonpath("pythonpath1")
    @binpath("binpath1")
    def test_ignore(self):
        """Test of ``ondouble=IGNORE``."""
        parser = argdispatch.ArgumentParser()
        sub = parser.add_subparsers()
        sub.add_function(function_foo, "foo")
        sub.add_function(function_foo, "foo", ondouble=argdispatch.IGNORE)
        sub.add_module("foo", ondouble=argdispatch.IGNORE)
        sub.add_executable("bin11", "foo", ondouble=argdispatch.IGNORE)

        with self.assertStdoutMatches(r"^\s*foo\s", count=1):
            with self.assertExit(0):
                parser.parse_args("--help".split())

    @pythonpath("pythonpath1")
    @binpath("binpath1")
    def test_error(self):
        """Test of ``ondouble=ERROR``."""
        parser = argdispatch.ArgumentParser()
        sub = parser.add_subparsers()
        sub.add_function(function_foo, "foo")
        with self.assertRaises(ValueError):
            sub.add_function(function_foo, "foo", ondouble=argdispatch.ERROR)
        with self.assertRaises(ValueError):
            sub.add_module("foo", ondouble=argdispatch.ERROR)
        with self.assertRaises(ValueError):
            sub.add_executable("bin11", "foo", ondouble=argdispatch.ERROR)

    def test_add_parser(self):
        """Test of ``ondouble`` argument with the ``add_parser`` method."""
        parser = argdispatch.ArgumentParser()
        sub = parser.add_subparsers()
        sub.add_function(function_foo, "foo")
        with self.subTest():
            with self.assertRaises(ValueError):
                sub.add_parser("foo", ondouble=argdispatch.ERROR)
        with self.subTest():
            sub.add_parser("foo", ondouble=argdispatch.IGNORE)
            with self.assertStdoutMatches(r"^\s*foo", count=1):
                with self.assertExit(0):
                    parser.parse_args("--help".split())

    @pythonpath("pythonpath1")
    @binpath("binpath1")
    def test_double(self):
        """Test of ``ondouble=DOUBLE``."""
        parser = argdispatch.ArgumentParser()
        sub = parser.add_subparsers()
        sub.add_function(function_foo, "foo")
        sub.add_function(function_foo, "foo", ondouble=argdispatch.DOUBLE)
        sub.add_module("foo", ondouble=argdispatch.DOUBLE)
        sub.add_executable("bin11", "foo", ondouble=argdispatch.DOUBLE)
        with self.assertStdoutMatches(r"^\s*foo", count=4):
            with self.assertExit(0):
                parser.parse_args("--help".split())

class TestHelp(TestArgparse):
    """Test that subcommand help works."""

    def test_function(self):
        """Test of the ``add_function`` method."""
        parser = argdispatch.ArgumentParser()
        sub = parser.add_subparsers()
        sub.add_function(function_foo, "foo1")
        sub.add_function(function_foo, "foo2", help="This is an hard-coded help")

        with self.subTest():
            with self.assertStdoutMatches("""foo1.*This is the docstring of function foo."""):
                with self.assertExit(0):
                    parser.parse_args("--help".split())

        with self.subTest():
            with self.assertStdoutMatches("""foo2.*This is an hard-coded help"""):
                with self.assertExit(0):
                    parser.parse_args("--help".split())

    def test_empty_help(self):
        """Test that automatic help works with empty or non-existent docstrings."""
        parser = argdispatch.ArgumentParser()
        sub = parser.add_subparsers()
        sub.add_function(function_nodocstring, "none")
        sub.add_function(function_emptydocstring, "empty")

        with self.subTest():
            with self.assertStdoutMatches(r"^\s*none\s*$"):
                with self.assertExit(0):
                    parser.parse_args("--help".split())

        with self.subTest():
            with self.assertStdoutMatches(r"^\s*empty\s*$"):
                with self.assertExit(0):
                    parser.parse_args("--help".split())

    def test_executable(self):
        """Test of help for ``add_executable`` method."""
        parser = self._ArgumentParser()
        sub = parser.add_subparsers()
        sub.add_executable("foo1")
        sub.add_executable("foo2", help="This is the help of foo2.")

        with self.subTest():
            with self.assertStdoutMatches(r"foo1"):
                with self.assertExit(0):
                    parser.parse_args("--help".split())

        with self.subTest():
            with self.assertStdoutMatches(r"foo2.*This is the help of foo2."):
                with self.assertExit(0):
                    parser.parse_args("--help".split())

    @pythonpath("pythonpath1", "pythonpath2.zip")
    def test_module(self):
        """Test of help for ``add_module`` method."""
        parser = argdispatch.ArgumentParser()
        sub = parser.add_subparsers()
        sub.add_module("foo", "foo1")
        sub.add_module("foo", "foo2", help="This is the help of foo2.")

        with self.subTest():
            with self.assertStdoutMatches("""foo1.*This is the docstring of module foo."""):
                with self.assertExit(0):
                    parser.parse_args("--help".split())

        with self.subTest():
            with self.assertStdoutMatches("""foo2"""):
                with self.assertExit(0):
                    parser.parse_args("--help".split())
