# Copyright Louis Paternault 2016
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

"""A replacement for `argparse` dispatching subcommand calls to functions, modules or executables.

Parsing arguments
-----------------

.. autoclass:: ArgumentParser()
   :no-members:

Adding subcommands
------------------

Adding subcommands to your program starts the same way as with `argparse
<https://docs.python.org/3.4/library/argparse.html#sub-commands>`_: one has to
call :meth:`ArgumentParser.add_subparsers`, and then call one of the methods of
the returned object. With :mod:`argparse`, this object only have one method
:meth:`~_SubCommandsDispatch.add_parser`. This module adds several new methods.

.. _ondouble:

Subcommands defined twice
^^^^^^^^^^^^^^^^^^^^^^^^^

Most of the methods creating subcommands accept an `ondouble` arguments, which
tells what to do when adding a subcommand that already exists:

- .. data:: ERROR

    Raise an :exc:`AttributeError` exception;

- .. data:: IGNORE

    The new subcommand is silently ignored;

- .. data:: DOUBLE

    The new subcommand is added to the parser, and :mod:`argparse` deals with
    it. This does not seem to be documented, but it seems that the parser then
    contains two subcommands with the same name.


.. _importerror:

Import errors
^^^^^^^^^^^^^

When using methods :meth:`~_SubCommandsDispatch.add_module` and
:meth:`~_SubCommandsDispatch.add_submodules`, modules are imported. But some
modules can be impossible to import because of errors. Both these methods have
the argument ``onerror`` to define what to do with such modules:

- .. data:: RAISE

    Raise an :exc:`ImportError` exception.

- .. data:: IGNORE

    Silently ignore this module.


.. _return:

Return value
^^^^^^^^^^^^

Unfortunately, different methods make :meth:`ArgumentParser.parse_args` return
different types of values. The two possible behaviours are illustrated below::

        >>> from argdispatch import ArgumentParser
        >>> def add(args):
        ...     print(int(args[0]) + int(args[1]))
        ...
        >>> parser = ArgumentParser()
        >>> subparsers = parser.add_subparsers()
        >>> parser1 = subparsers.add_parser("foo")
        >>> parser1.add_argument("--arg")
        _StoreAction(
                option_strings=['--arg'], dest='arg', nargs=None, const=None, default=None,
                type=None, choices=None, help=None, metavar=None,
                )
        >>> subparsers.add_function(add)
        >>> parser.parse_args("foo --arg 3".split())
        Namespace(arg='3')
        >>> parser.parse_args("add 3 4".split())
        7

The ``NameSpace(...)`` is the object *returned* by
:meth:`~ArgumentParser.parse_args`, while the ``7`` is *printed* by function,
and the interpreter then exits (by calling :func:`sys.exit`).

Call to :meth:`~ArgumentParser.parse_args`, when parsing a subcommand defined by:

- legacy method :meth:`~_SubCommandsDispatch.add_parser`, returns a
  :class:`~ArgumentParser.Namespace` (this method is (almost) unchanged
  compared to :mod:`argparse`);
- new methods do not return anything, but exit the program with :meth:`sys.exit`.

Thus, we do recommand not to mix them, to make source code easier to read, but
technically, it is possible.

Subcommand definition
^^^^^^^^^^^^^^^^^^^^^

Here are all the :class:`_SubCommandsDispatch` commands to define subcommands.

- Legacy subcommand

    .. automethod:: _SubCommandsDispatch.add_parser

- Function subcommand

    .. automethod:: _SubCommandsDispatch.add_function

- Module subcommands

    .. automethod:: _SubCommandsDispatch.add_module

    .. automethod:: _SubCommandsDispatch.add_submodules

- Executable subcommands

    .. automethod:: _SubCommandsDispatch.add_executable

    .. automethod:: _SubCommandsDispatch.add_pattern_executables

    .. automethod:: _SubCommandsDispatch.add_prefix_executables
"""

from argparse import * # pylint: disable=wildcard-import
import argparse
import contextlib
import enum
import importlib
import os
import pkgutil
import re
import runpy
import subprocess
import sys

VERSION = "0.1.1"
__AUTHOR__ = "Louis Paternault (spalax@gresille.org)"
__COPYRIGHT__ = "(C) 2016 Louis Paternault. GNU GPL 3 or later."
__all__ = argparse.__all__ + ['ERROR', 'IGNORE', 'DOUBLE', 'RAISE']

################################################################################
# Constants

class _Constants(enum.Enum):
    """Subclass of :class:`enum.Enum` to display only the constant name in the documentation."""
    ERROR = 1
    IGNORE = 2
    DOUBLE = 3
    RAISE = 4

    def __repr__(self):
        return self.name

ERROR = _Constants.ERROR
IGNORE = _Constants.IGNORE
DOUBLE = _Constants.DOUBLE
RAISE = _Constants.RAISE

################################################################################
# Misc utilities

def _first_non_empty_line(text):
    if text is None:
        return ""
    try:
        return [line.strip() for line in text.split("\n") if line.strip()][0]
    except IndexError:
        return ""

@contextlib.contextmanager
def _update_sys(**kwargs):
    old = {}
    for attr in kwargs:
        old[attr] = getattr(sys, attr)
        setattr(sys, attr, kwargs[attr])
    try:
        yield
    except Exception:
        raise
    finally:
        for attr in old:
            setattr(sys, attr, old[attr])

def _make_bin_executable(executable):
    """Return a function that, when called, execute the given executable"""
    def run(args):
        """Call executable with given arguments"""
        return subprocess.call([executable] + args)
    return run

def _make_module_executable(module, path=None):
    """Return a function that, when called, execute the given module"""
    if path is None:
        path = sys.path
    def run(args):
        """Call the module with given arguments"""
        with _update_sys(path=path, argv=[module] + args):
            runpy.run_module(module, run_name="__main__")
            return 0
    return run

def _is_package(name):
    """Return ``True`` iff module is a package."""
    spec = importlib.util.find_spec(name)
    if spec is None:
        raise ImportError("No module named '{}'.".format(name))
    return spec.submodule_search_locations is not None

################################################################################
# Redefinition of some argparse classes

class ArgumentParser(ArgumentParser): # pylint: disable=function-redefined
    """Create a new :class:`ArgumentParser` object.

    There is no visible changes compared to :class:`argparse.ArgumentParser`.
    For internal changes, see :ref:`advanced`.
    """

    def add_subparsers(self, *args, **kwargs):
        if "action" not in kwargs:
            kwargs['action'] = _SubCommandsDispatch
        return super().add_subparsers(*args, **kwargs)

class _SubCommandsDispatch(argparse._SubParsersAction): # pylint: disable=protected-access
    """Object returned by the :meth:`argparse.ArgumentParser.add_subparsers` method.

    Its methods :meth:`add_*` are used to add subcommands to the parser.
    """

    def __call__(self, *args, **kwargs):
        if self._name_dispatcher_map.get(args[2][0], None) is not None:
            sys.exit(self._name_dispatcher_map[args[2][0]](args[2][1:]))
        return super().__call__(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._name_dispatcher_map = {}

    def add_parser(self, *args, **kwargs):
        """Add a subparser, and return an :class:`ArgumentParser` object.

        This is the same method as the original :mod:`argparse`, excepted that
        an ``ondouble`` argument has been added.

        :param ondouble: See :ref:`ondouble`. Default is :data:`DOUBLE`.
        """
        ondouble = kwargs.pop('ondouble', DOUBLE)
        if args[0] in self._name_dispatcher_map:
            if ondouble == IGNORE:
                return
            elif ondouble == ERROR:
                raise ValueError("Subcommand '{}' is already defined.".format(args[0]))
            elif ondouble == DOUBLE:
                pass
        else:
            self._name_dispatcher_map[args[0]] = None
        return super().add_parser(*args, **kwargs)

    def add_executable(self, executable, command=None, *, help=None, ondouble=ERROR):
        """Add a subcommand matching a system executable.

        :param str executable: Name of the executable to use.
        :param str command: Name of the subcommand. If ``None``, the executable is used.
        :param str help: A brief description of what the subcommand does. If
            `None`, use an empty help.
        :param ondouble: See :ref:`ondouble`. Default is :data:`ERROR`.
        """
        # pylint: disable=redefined-builtin
        if command is None:
            command = executable
        if command in self._name_dispatcher_map:
            if ondouble == IGNORE:
                return
            elif ondouble == ERROR:
                raise ValueError("Subcommand '{}' is already defined.".format(command))
            elif ondouble == DOUBLE:
                pass
        else:
            self._name_dispatcher_map[command] = _make_bin_executable(executable)
        self.add_parser(command, help=help, ondouble=DOUBLE)

    def add_pattern_executables(self, pattern, *, path=None, ondouble=IGNORE):
        """Add all the executables in path matching the regular expression.

        If `pattern` contains a group named `command`, this is used as the
        subcommand name. Otherwise, the executable name is used.

        :param str pattern: Regular expression defining the executables to add as subcommand.
        :param iterable path: Iterator on paths in which executable has to been
            searched for. If `None`, use the ``PATH`` environment variable.
            This arguments *replaces* the ``PATH`` environment variable: if you
            want to extend it, use ``":".join(["my/custom", "path",
            os.environ.get("PATH", "")])``.
        :param ondouble: See :ref:`ondouble`. Default is :data:`IGNORE`.
        """
        executables = set()
        if path is None:
            path = os.environ['PATH'].split(":")
        compiled = re.compile(pattern)
        for pathitem in path:
            if not os.path.isdir(pathitem):
                continue
            for filename in os.listdir(pathitem):
                fullpath = os.path.join(pathitem, filename)
                if fullpath in executables:
                    continue
                if os.path.isfile(fullpath):
                    if os.access(fullpath, os.X_OK):
                        match = compiled.match(filename)
                        if match:
                            if "command" in match.groupdict():
                                command = match.groupdict()['command']
                            else:
                                command = filename
                            executables.add(fullpath)
                            self.add_executable(fullpath, command, ondouble=ondouble)

    def add_prefix_executables(self, prefix, *, path=None, ondouble=IGNORE):
        """Add all the executables starting with ``prefix``

        The subcommand name used is the executable name, without the prefix.

        :param prefix: Common prefix of all the executables to use as subcommands.
        :param iterable path: Iterator on paths in which executable has to been
            searched for. See
            :meth:`~_SubCommandsDispatch.add_pattern_executables` for more
            information.
        :param ondouble: See :ref:`ondouble`. Default is :data:`IGNORE`.
        """
        return self.add_pattern_executables(
            r'^{}(?P<command>.*)$'.format(prefix),
            path=path,
            ondouble=ondouble,
            )

    def add_function(self, function, command=None, *, help=None, ondouble=ERROR):
        """Add a subcommand matching a python function.

        :param function: Function to use.
        :param str command: Name of the subcommand. If ``None``, the function name is used.
        :param str help: A brief description of what the subcommand does. If
            `None`, use the first non-empty line of the function docstring.
        :param ondouble: See :ref:`ondouble`. Default is :data:`ERROR`.

        This function is approximatively called using::

            sys.exit(function(args))

        It must either return something which will be transimtted to
        :func:`sys.exit`, or directly exit using :meth:`sys.exit`. If it raises
        an exception, this exception is not catched by :mod:`argdispatch`.
        """
        # pylint: disable=redefined-builtin
        if command is None:
            command = function.__name__
        if help is None:
            help = _first_non_empty_line(function.__doc__)
        if command in self._name_dispatcher_map:
            if ondouble == IGNORE:
                return
            elif ondouble == ERROR:
                raise ValueError("Subcommand '{}' is already defined.".format(command))
            elif ondouble == DOUBLE:
                pass
        else:
            self._name_dispatcher_map[command] = function
        self.add_parser(command, help=help, ondouble=DOUBLE)

    def add_module(self, module, command=None, *, path=None, help=None, ondouble=ERROR, onerror=RAISE): # pylint: disable=line-too-long
        """Add a subcommand matching a python module.

        When such a subcommand is parsed, ``python -m module`` is called with
        the remaining arguments.

        :param str module: Module or package to use. If a package, the
            ``__main__`` submodule is used.
        :param str command: Name of the subcommand. If ``None``, the module name is used.
        :param iterable path: Iterator on paths in which module has to been
            searched for. If `None`, use :data:`sys.path`. This arguments
            *replaces* :data:`sys.path`: if you want to extend it, use
            ``sys.path + ["my/custom", "path"]``.
        :param str help: A brief description of what the subcommand does. If
            `None`, use the first non-empty line of the module docstring.
        :param ondouble: See :ref:`ondouble`. Default is :data:`ERROR`.
        :param onerror: See :ref:`importerror`. Default is :data:`RAISE`.
        """
        # pylint: disable=redefined-builtin, too-many-branches
        if path is None:
            path = sys.path

        try:
            with _update_sys(path=path):
                ispkg = _is_package(module)
                if ispkg:
                    module = "{}.__main__".format(module)
                imported = importlib.import_module(module)
        except Exception as error: # pylint: disable=broad-except
            if onerror == RAISE:
                raise ImportError("Cannot load module '{}': {}.".format(
                    '{}'.format(module),
                    str(error)
                    ))
            if onerror == IGNORE:
                return
        if command is None:
            if ispkg:
                command = imported.__name__[:-len(".__main__")]
            else:
                command = imported.__name__
        if help is None:
            help = _first_non_empty_line(imported.__doc__)
        if command in self._name_dispatcher_map:
            if ondouble == IGNORE:
                return
            elif ondouble == ERROR:
                raise ValueError("Subcommand '{}' is already defined.".format(command))
            elif ondouble == DOUBLE:
                pass
        else:
            self._name_dispatcher_map[command] = _make_module_executable(module)
        self.add_parser(command, help=help, ondouble=DOUBLE)

    def add_submodules(self, module, *, path=None, ondouble=IGNORE, onerror=IGNORE):
        """Add subcommands matching `module`'s submodules.

        The modules that are used as subcommands are submodules of `module`
        (without recursion), that themselves contain a ``__main__`` submodule.

        :param str module: Module to use.
        :param iterable path: Iterator on paths in which module has to been
            searched for. See :meth:`~_SubCommandsDispatch.add_module` for more
            information.
        :param ondouble: See :ref:`ondouble`. Default is :data:`IGNORE`.
        :param onerror: See :ref:`importerror`. Default is :data:`IGNORE`.
        """
        if module.startswith("."):
            raise NotImplementedError("Method does not support (yet?) relative modules")
        if path is None:
            path = sys.path
        subpath = [
            os.path.join(path, *module.split("."))
            for path in path
            ]
        for __finder, name, ispkg in pkgutil.iter_modules(subpath):
            if ispkg:
                if importlib.util.find_spec("{}.{}.__main__".format(module, name)) is not None:
                    self.add_module(
                        "{}.{}".format(module, name),
                        command=name,
                        ondouble=ondouble,
                        onerror=onerror,
                        )
