#! /usr/bin/env python
# coding: utf-8

"""Command Line Option Processor.

Provides class clop.Clop, which takes a command line option/args specification
and processes a command line against it.
"""

from __future__ import print_function

import string
import sys


class Clop(object):
    """A Clop object holds legal options for a command line,
    processes a supplied command line against the legal options,
    and makes the results available.
    A formatted help string of options for the whole command
    can also be produced.
    """

    def __init__(self):
        # Required options and their definitions.
        self.required = {}

        # Optional options and their definitions.
        self.optional = {}


    def addOptionDef(self,
            letter=None,
            required=None,
            numArgs=None,
            help=None):
        """Add a single option definition to a Clop object.

        All arguments must be supplied.

        Example:
          clp.addOptionDef(letter='o',
              required=True,
              numArgs=float('inf'),
              help='help for o')

        letter:
          The command line option letter for this option, without the '-'.
        required:
          True = This option must appear on the command line.
          False = This option is optional.
        numArgs:
          Number of args that must/may appear after an option.
          numArgs = any int >= 0: exactly that number of args must follow the option.
          numArgs = float('inf'): any number of args allowed, 0 or more.
        help:
          Short description of this option.
          Part of a larger help string for the overall command.

        Exceptions:
            TypeError:
                - Missing argument. (None is type NoneType)
                - Wrong argument type.
            ValueError:
                - letter has already been seen by this Clop object.
                - letter.isalpha()is False.
                - numArgs is not int >= 0, or infinity (float('inf')).
        """

        letterError = 'letter: Single option letter must be supplied.'
        if type(letter) != str:
            raise TypeError(letterError)
        if len(letter) != 1 or not letter.isalpha():
            raise ValueError(letterError)

        requiredError = 'required: True or False must be supplied.'
        if type(required) != bool:
            raise TypeError(requiredError)

        numArgsError = 'numArgs: int >= 0 or float(\'inf\') must be supplied.'
        if type(numArgs) != int and type(numArgs) != float:
            raise TypeError(numArgsError)
        if (numArgs < 0 or
                (type(numArgs) == float and numArgs != float('inf'))):
            raise ValueError(numArgsError)

        helpError = 'help: must be string.'
        if type(help) != str:
            raise TypeError(helpError)

        if letter in self.required or letter in self.optional:
            raise ValueError('Option letter ' + letter + ' already seen.')

        target = self.required if required else self.optional
        target[letter] = {
            'numArgs': numArgs,
            'help': help}


    def processCmdLine(self, cmdLine=None):
        """Break up the cmdLine to its options and arguments.
        Check opts and args against self.required and self.optional.

        cmdLine is assumed to be a copy of sys.argv[1:].

        Return a dictionary of {letter: args}
        where args is a list of arguments found after a command line option.

        Return empty dictionary if:
          - not cmdLine

        If you build your own cmdLine list, note:
        - All items on the list must be strings, just like sys.argv.
        - Don't forget the dash in front of letter options.

        Exceptions:
          TypeError:
            - Anything in cmdLine is not string.
          ValueError:
            - Badly formed option or argument.
            - Required option missing.
            - Option is neither required or optional (not allowed).
            - Wrong number of arguments for an option.
        """
        
        if not cmdLine and not self.required:
            return {}
        
        if not cmdLine and self.required:
            raise ValueError('Empty cmdLine and required options.')

        if type(cmdLine) != list:
            raise TypeError('cmdLine must be list of strings.')

        for i in cmdLine:
            if type(i) != str:
                raise TypeError(
                    'All command line options and arguments must be strings.')

        # Easier if we can assume this.
        if not cmdLine[0].startswith('-'):
            raise ValueError(' '.join([
                'The first thing after the program name',
                'must be a single letter option like -o, not', cmdLine[0] ]))

        # Detect badly formed options and arguments.
        for i in cmdLine:
            if i[0] == '-':
                if len(i) != 2 or i[1] == '-':
                    raise ValueError(' '.join([
                        'Options can only be a dash followed by a letter,',
                        'not', i ]))
            elif '-' in i:
                raise ValueError(' '.join(([
                    'Dash only at front of option, not', i])))

        # Remove first option's leading dash,
        # to prevent '' at [0] after split on '-'.
        # Make a list of strings, each string is an option and any arguments.
        # '-o', 'one', 'two' becomes 'o one two '.
        cmdLine[0] = cmdLine[0][1]
        cmdLine = ' '.join(cmdLine).split('-')

        # Dictionary of options and arguments.
        # 'o one two ' becomes 'o': ['one', 'two']
        # optArgs returned if remaining checks pass.
        optArgs = {x.strip()[0]: x.strip()[1:].split() for x in cmdLine}
        present = set(optArgs.keys())

        required = set(self.required.keys())
        optional = set(self.optional.keys())
        allowed = required | optional

        missing = required - present
        if missing:
            raise ValueError(' '.join([
                'Required options are missing:',
                ', '.join(sorted(missing)) ]))

        unallowed = present - allowed
        if unallowed:
            raise ValueError(' '.join([
                'Unallowed options supplied:',
                ', '.join(sorted(unallowed)) ]))
        
        all = dict(list(self.required.items()) + list(self.optional.items()))
        for o in present:
            defNum = all[o]['numArgs']
            argNum = len(optArgs[o])

            if defNum != float('inf') and defNum != argNum:
                raise ValueError(' '.join([
                    'Option', o,
                    'requires exactly', str(defNum), 'arguments,',
                    'received', str(argNum) ]))

        return optArgs


    def helpString(self, preamble = None):
        """Return a simple help string for all options,
        using their help strings.

        Preamble included if preamble is not None.
        preamble might be just the program name,
        or the name and a short description of the program,
        or an empty string.
        Or preamble could be left None.

        Exceptions:
          TypeError:
            - preamble != None, or preamble not string.
        """

        if preamble != None and type(preamble) != str:
                raise TypeError('preamble must be None or string.')

        all = dict(list(self.required.items()) + list(self.optional.items()))
        def formatOptions(optList):
            optStr = ''
            for o in optList:
                numArgs = all[o]['numArgs']
                if numArgs == float('inf'):
                    numArgs = '0 or more\n'
                else:
                    numArgs = 'Exactly ' + str(numArgs) + '\n'

                optStr += o + ': ' + all[o]['help'] + '\n'
                optStr += '  Allowed arguments: '
                optStr += numArgs

            return optStr

        requiredOpts = sorted(self.required.keys())
        requiredHelp = formatOptions(requiredOpts)

        optionalOpts = sorted(self.optional.keys())
        optionalHelp = formatOptions(optionalOpts)

        helpStr = preamble.strip('\n') + '\n' if preamble else ''

        if requiredHelp:
            helpStr += '\nREQUIRED OPTIONS:\n'
            helpStr += requiredHelp

        if optionalHelp:
            helpStr += '\nOPTIONAL OPTIONS:\n'
            helpStr += optionalHelp

        return helpStr


def main(cmdLineOptions):
    """Smoke test. Brief demo of class Clop()"""

    print('\nTest any command line, against non-Clop command line chopping,')
    print('and against a Clop option specification.\n')

    print('Incoming command line options:\n', cmdLineOptions)

    print('\n----- Simple command line chopping: -----\n')

    # The following three lines is all of what Clop() does,
    # but without any error checking, features or help strings.
    # For entertainment purposes only.

    argList = ' '.join(cmdLineOptions).split('-')
    argList = [x for x in argList if x != '']
    optArgs = {x[0]: x[1:].strip().split() for x in argList}

    print(optArgs, '\n')

    # "And now ..."

    print('\n----- Clop command line processing: -----\n')

    clp = Clop()

    clp.addOptionDef(letter = 'k',
        required = True,
        numArgs = 3,
        help = 'Help for option k')

    clp.addOptionDef(letter = 'm',
        required = True,
        numArgs = 1,
        help = 'Help for option m')

    clp.addOptionDef(letter = 'n',
        required = True,
        numArgs = float('inf'),
        help = 'Help for option n')

    clp.addOptionDef(letter = 'o',
        required = False,
        numArgs = 0,
        help = 'Help for option o')

    clp.addOptionDef(letter = 'p',
        required = False,
        numArgs = 1,
        help = 'Help for option p')

    clp.addOptionDef(letter = 'q',
        required = False,
        numArgs = float('inf'),
        help = 'Help for option q')

    print(clp.helpString('clop:\nShort demo of the clop module.'))

    try:
        optArgs = clp.processCmdLine(sys.argv[1:])
    except Exception as exp:
        print(exp)
        sys.exit(2)

    print('Using Clop() command line handling:')
    print(optArgs)
    print

__all__ = ['Clop', 'main']

if __name__ == '__main__':
    main(sys.argv[1:])
