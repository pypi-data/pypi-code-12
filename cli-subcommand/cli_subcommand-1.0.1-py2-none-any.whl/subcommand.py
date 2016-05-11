# -*- coding: utf-8 -*-

from __future__ import print_function


__title__ = 'subcommand'
__version__ = '1.0.1'
__author__ = 'Derrick J. Wippler'
__license__ = 'Apache 2.0'


from argparse import ArgumentParser, RawDescriptionHelpFormatter
from collections import namedtuple
from os.path import basename
from textwrap import dedent

import inspect
import sys
import re


Option = namedtuple('Option', ['args', 'kwargs'])


def opt(*args, **kwargs):
    """Use this decorator to add options to a sub command method. This
    decorator accepts the same arguments as `ArgumentParser.add_argument
    <https://docs.python.org/3/library/argparse.html#the-add-argument-method>`_

        >>> @opt('--opt-arg', help="This is my optional arg")
        >>> @opt('pos-arg', help="This is my positional arg")
        >>> def test_sub_command(self, pos_arg=None, opt_arg=None):
        >>>   print(pos_arg, opt_arg)
    """
    def decorator(method):
        if not hasattr(method, 'options'):
            method.options = []
        if args:
            # Append the option to our option list
            method.options.append(Option(args, kwargs))
        # No need to wrap, only adding an attr to the method
        return method
    return decorator


def noargs(method):
    """Use this decorator to denote the sub command has no args

        >>> @noargs
        >>> def test_sub_command(self):
        >>>     print("noargs subcommand")
    """
    method.options = []
    return method



class SubParser(object):
    """Collects Command() objects and parse the commandline

        >>> parser = SubParser([TestCommands()],
        ...                            desc="Test Description")
        >>> parser.run(['prog', 'test', 'command',
        ...             'arg1', '--opt-arg', 'arg2'])
    """
    def __init__(self, sub_commands, desc=None):
        self.sub_commands = self._build_dict(sub_commands)
        self.prog = None
        self.desc = desc

    def _build_dict(self, sub_commands):
        """Given a list of :class:`Commands` objects return a dict mapping of
        subcommand name and objects
        """
        result = {}
        for cmd in sub_commands:
            # If command is just an instance of 'object', ignore the cmd
            if cmd.__class__.__name__ == 'object':
                continue

            name = getattr(cmd, '_name', None)
            if not name:
                raise RuntimeError(
                    "object '%s' has no attribute '_name'; "
                    "please give your Commands class a name" % cmd
                )
            result[name] = cmd
        return result

    def run(self, args=None, prog=None):
        """Parse the command line arguments passed and execute the command
        requested, if no matching command is found or no argument display help
        and exit
        """
        # use sys.argv if not supplied
        if not args:
            prog = basename(sys.argv[0])
            args = sys.argv[1:]
        self.prog = prog

        # If completion token found in args
        if '--bash-completion' in args:
            return self.bash_completion(args)

        # If bash completion script requested
        if '--bash-completion-script' in args:
            return self.bash_completion_script(prog)

        # Find a subcommand in the arguments
        for index, arg in enumerate(args):
            if arg in self.sub_commands.keys():
                # Remove the sub command argument
                args.pop(index)
                # Run the sub-command passing the remaining arguments
                return self.sub_commands[arg](args, prog)

        # Unable to find a suitable sub-command
        return self.help()

    def bash_completion_script(self, prog):
        """ Output a bash completion script to stdout. To Create a bash
        completion script on ubuntu and maybe other distros::

            ./my-script.py --bash-completion-script \\
                    > /etc/bash_completion.d/my-script.py
        """
        print('_%(prog)s() {\n'\
            '  local cur="${COMP_WORDS[COMP_CWORD]}"\n'\
            '  local list=$(%(prog)s --bash-completion $COMP_LINE)\n'\
            '  COMPREPLY=($(compgen -W "$list" $cur))\n'\
            '}\n'\
            'complete -F _%(prog)s %(prog)s\n' % locals())

    def bash_completion(self, args):
        """Used by the bash completion script to output completion candidates.
        The args passed by the bash completion script to this command are as
        follows::

            args = ['--bash-completion', '%prog', 'sub-cmd', 'command']
        """
        try:
            # If a subcommand is already present
            if args[2] in self.sub_commands.keys():
                # Have the subcommand print out all possible commands
                return self.sub_commands[args[2]].bash_completion()
        except (KeyError, IndexError):
            pass

        # Print out all the possible sub command names
        print(' '.join(self.sub_commands.keys()))
        return 0

    def help(self):
        """Print help message and exit"""
        print("Usage: %s <command> [-h]\n" % self.prog)
        if self.desc:
            print(self.desc + '\n')

        print("Available Commands:")
        for name, command in self.sub_commands.items():
            print("  ", name)
            # TODO: Print some help message for the commands?
        return 1


class Parser(SubParser):
    """
        >>> parser = CommandParser([TestCommands()], desc="")
        >>> return parser.run()

    """
    def __init__(self, commands, desc=None):
        self.sub_commands = self._build_dict(commands)
        self.prog = None
        self.desc = desc

    def _build_dict(self, commands):
        """Given a list of :class:`Commands` objects return a dict mapping of
        method names and objects
        """
        result = {}
        # get a listing of all the methods
        for cmd in commands:
            for (name, method) in cmd._commands.items():
                result[name] = MethodWrapper(cmd, method)
        return result


class Commands(object):
    """This is where you define all the commands that are accessed via the
    command line. Every command object must have a `_name` defined if used by
    the :class:`SubParser`

        >>> class TestCommands(Commands):
        ...      _name = 'test'
        ...      @opt('pos-arg', help="This is my positional arg")
        ...      @opt('--opt-arg', help="This is my optional arg")
        ...      def command1(self, pos_arg=None, opt_arg=None):
        ...         print('cmd with opts %s, %s' % pos_arg, opt_arg)
        ...      @noargs
        ...      def command2(self):
        ...         print('cmd with no args')
    """
    def __init__(self):
        # Return a dict of all methods with the options attribute
        self._commands = self._methods_with_opts()
        self.prog = None

    def pre_command(self):
        """This method is called prior to calling the command specified via the
        command line. Use it to initialize common code within your
        :class:`Commands` object

            >>> class TestCommands(Commands):
            ...      _name = 'test'
            ...      def pre_command(self):
            ...         print("I get run first")
            ...      @noargs
            ...      def command(self):
            ...         print("Run my command")
            >>> parser = SubParser([TestCommands()], desc="")
            >>> parser.run(['prog', 'test', 'command'])
            I get run first
            Run my command
        """
        pass

    def bash_completion(self):
        """By default returns all the commands defined for this
        :class:`Commands` object. This method is invoked when --bash-completion
        is called for a specific subcommand. This can be overidden by the
        implementor to return custom behaivor """
        print(' '.join(self._commands.keys()), end=' ')
        return 0

    def remove(self, haystack, needles):
        """This method eliminates un-wanted keyword arguments

            >>> if args['debug']:
            >>>     print "print debug output"
            >>> # Remove the debug and verbose keys
            >>> kwargs = self.remove(args, ['verbose', 'debug'])
            >>> self.call_some_method(**kwargs)
        """
        result = {}
        for key, value in haystack.items():
            if key not in needles:
                result[key] = value
        return result

    def split(self, args, positionals):
        """Splits keys specified into separate lists, this method is commonly
        used to split positional arguments from keyword arguments

            >>> args, kwargs = self.split(args, ['my', 'list', 'of',
            ...                                  'positional', 'args'])
        """
        kwargs = args.copy()
        args = {}
        for key, value in kwargs.items():
            # Split out the positional args from the kwargs
            if key in positionals:
                del kwargs[key]
                args[key] = value
            # Remove the kwarg if its None, this allows
            # python default values to work properly
            if value is None:
                del kwargs[key]
        return (args, kwargs)

    def opt(self, *args, **kwargs):
        """Use this method to define :class:`Commands` options that are common to each
        command

        >>> class TestCommands(Commands):
        ...      _name = 'test'
        ...      def __init__(self):
        ...         self.opt('-d', '--debug', action='store_const',
        ...                  const=True, default=False,
        ...                  help="Print debug to stdout")
        ...      @noargs
        ...      def command1(self):
        ...         print(self.debug)
        ...      @noargs
        ...      def command2(self):
        ...         print(self.debug)
        """
        if not hasattr(self, 'globals'):
            self.globals = []
        self.globals.append(Option(args, kwargs))

    def _methods_with_opts(self):
        """Collect all the methods in this object that have options and return
        a dict with the converted name and method """
        result = {}
        # get a listing of all the methods
        for name in dir(self):
            if name.startswith('__'):
                continue
            method = getattr(self, name)
            # If the method has an options attribute
            if hasattr(method, 'options'):
                name = re.sub('_', '-', name)
                result[name] = method
        return result

    def _call_method(self, args, method):
        """Given a method and the remaining arguments call the method"""
        # Parse the arguments
        args = self._parse_args(method, args)
        # Determine the acceptable arguments
        (kwargs, unused) = self._acceptable_args(self._get_args(method),
                                                args)
        # Attach the unused options as class variables
        for key, value in unused.items():
            # Don't overwrite a method or some such
            if not hasattr(self, key):
                setattr(self, key, value)

        # If all args are rolled into 'args' the user should still
        # expect to find the args attached to the class
        if len(kwargs) == 1 and 'args' in kwargs:
            for key, value in kwargs['args'].items():
                # Don't overwrite a method or some such
                if not hasattr(self, key):
                    setattr(self, key, value)

        # Call the pre_command method now that args have been parsed
        self.pre_command()
        # Call the command with the command
        # line args as method arguments
        return method(**kwargs)

    def __call__(self, args, prog):
        """ Figure out which command this sub-command should be run then pass
        the arguments to the commands parser
        """
        self.prog = prog
        for index, arg in enumerate(args):
            # Find a command in the arguments
            if arg in self._commands.keys():
                # Get the method for the command
                method = self._commands[arg]
                # Remove the command from the args
                args.pop(index)
                # Call the method with the remaining arguments
                return self._call_method(args, method)

        # Unable to find the command
        return self.help()

    def _parse_args(self, method, args):
        """Using `ArgumentParser
        <https://docs.python.org/3/library/argparse.html>`_
        parse the command line arguments and return the name of the
        subcommand requested
        """
        # create an argument parser
        parser = ArgumentParser(prog=method.__name__,
                                description=dedent(method.__doc__ or ''),
                                formatter_class=RawDescriptionHelpFormatter)
        # Add method options to the subparser
        for opt in method.options:
            parser.add_argument(*opt.args, **opt.kwargs)
        # Add global options to the subparser

        if hasattr(self, 'globals'):
            for opt in self.globals:
                parser.add_argument(*opt.args, **opt.kwargs)

        results = {}
        args = vars(parser.parse_args(args))
        # Convert dashes to underscore
        for key, value in args.items():
            results[re.sub('-', '_', key)] = value
        return results

    def help(self):
        """Print a help message with a list of available commands to choose
        from and return
        """
        print("Usage: %s %s <command> [-h]\n" % (self.prog, self._name))
        if self.__doc__:
            stripped = self.__doc__.strip('\n| ')
            print(re.sub(' ' * 4, '', stripped))

        print("\nAvailable Commands:")
        for name, command in self._commands.items():
            print("  ", name)
            # print "  ", command.__doc__.strip('\n')
        return 1

    def _get_args(self, func):
        """Get the arguments of a method and return it as a dictionary with
        the supplied defaults, method arguments with no default are assigned
        None """
        def reverse(iterable):
            if iterable:
                iterable = list(iterable)
                while len(iterable):
                    yield iterable.pop()

        args, varargs, varkw, defaults = inspect.getargspec(func)
        result = {}
        for default in reverse(defaults):
            result[args.pop()] = default

        for arg in reverse(args):
            if arg == 'self':
                continue
            result[arg] = None

        return result

    def _acceptable_args(self, _to, _from):
        _other = {}
        # If the method has a variable called 'args'
        # then assign all the arguments to 'args'
        if 'args' in _to:
            _to['args'] = _from
            return (_to, {})

        # Collect arguments that will not
        # be passed into the method
        for key, value in _from.items():
            if key not in _to:
                _other[key] = _from[key]

        # Collect arguments that will be
        # passed to the method
        for key, value in list(_to.items()):
            if key in _from:
                _to[key] = _from[key]
            # Remove arguments that have no value this allows
            # default values on the method signature to take effect
            if _to[key] is None:
                del _to[key]
        return (_to, _other)


class MethodWrapper(Commands):
    """Wrap :class:`Commands` so it can be passed to the
    :class:`CommandParser`"""

    def __init__(self, cmd, method):
        # Copy over all the attr of the cmd class
        # since we are taking it's place
        for name in dir(self):
            if name.startswith('__'):
                continue
            setattr(self, name, getattr(cmd, name))
        # Overide the commands, since we only
        # want to execute 1 method
        self._commands = method

    def __call__(self, args, prog):
        """Figure out which command for this sub-command should be run then
        pass the arguments to the commands parser
        """
        self.prog = prog
        return self._call_method(args, self._commands)
