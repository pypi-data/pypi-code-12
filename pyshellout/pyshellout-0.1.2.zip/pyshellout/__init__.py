"""
Thin convenience wrappers for shelling out commands easily from python.
"""
from subprocess import run, PIPE
import os
import sys

# Python 2/3 compatibility
try:
    input = raw_input
except NameError:
    pass


def out(command, *args, input=None, verbose=False, stdout=sys.stdout, stderr=sys.stderr, **kwargs):
    """
    Execute given command, with given input, formatted with given arguments, and send output to
    stdout and stderr.
    Return the return code of the subprocess.
    """
    shellcommand = command.format(*args, **kwargs)
    if verbose:
        print('Running shell command: {}'.format(shellcommand))
    result = run(shellcommand, input=input, stdout=stdout,
                 stderr=stderr, universal_newlines=True, shell=True)
    return result.returncode


def get(command, *args, input=None, verbose=False, stdout=PIPE, stderr=PIPE, **kwargs):
    """
    Execute given command, with given input, formatted with given arguments, and return output
    as a ShellString.
    """
    shellcommand = command.format(*args, **kwargs)
    if verbose:
        print('Running shell command: {}'.format(shellcommand))
    result = run(shellcommand, input=input, stdout=stdout,
                 stderr=stderr, universal_newlines=True, shell=True)
    return ShellString(result.stdout + result.stderr)


def confirm(msg, *args, **kwargs):
    """
    Prompt user with a message and wait for user to type 'y' of 'n'.
    Return True if 'y', False if 'n'.
    """
    while 1:
        reply = input(msg.format(*args, **kwargs) + ' [y/n]')
        if reply == 'y':
            return True
        if reply == 'n':
            return False
        print("Please type 'y' or 'n'.")


class ShellString(str):

    """
    String derivative with a special access attributes.

    These are normal strings, but with the special attributes:

        .n (or .nlist): value as list (split on newlines).
        .z (or .zlist): value as list (split on null bytes).
        .s (or .splist): value as list (split on spaces).
        .p (or .paths): list of path objects (requires path.py package)

    Any values which require transformations are computed only once and
    cached.

    Such strings are very useful to efficiently interact with the shell, which
    typically only understands whitespace-separated options for commands.
    """

    def get_nlist(self):
        try:
            return self.__nlist
        except AttributeError:
            self.__nlist = ShellList(self.split('\n'))
            return self.__nlist

    n = nlist = property(get_nlist)

    def get_zlist(self):
        try:
            return self.__zlist
        except AttributeError:
            self.__zlist = ShellList(self.split('\x00'))
            return self.__zlist

    z = zlist = property(get_zlist)

    def get_splist(self):
        try:
            return self.__splist
        except AttributeError:
            self.__splist = ShellList(self.split(' '))
            return self.__splist

    s = splist = property(get_splist)

    def get_paths(self):
        from path import path
        try:
            return self.__paths
        except AttributeError:
            self.__paths = ShellList([path(p) for p in self.n if os.path.exists(p)])
            return self.__paths

    p = paths = property(get_paths)


class ShellList(list):
    """
    List derivative with a special access attributes.

    These are normal lists, but with the special attributes:

    * .n (or .nlstr): value as a string, joined on newlines.
    * .z (or .zstr): value as a string, joined on null bytes.
    * .s (or .spstr): value as a string, joined on spaces.
    * .p (or .paths): list of path objects (requires path.py package)

    Any values which require transformations are computed only once and
    cached.
    """

    def get_zstr(self):
        try:
            return self.__zstr
        except AttributeError:
            self.__zstr = ShellString('\x00'.join(self))
            return self.__zstr

    z = zstr = property(get_zstr)

    def get_spstr(self):
        try:
            return self.__spstr
        except AttributeError:
            self.__spstr = ShellString(' '.join(self))
            return self.__spstr

    s = spstr = property(get_spstr)

    def get_nlstr(self):
        try:
            return self.__nlstr
        except AttributeError:
            self.__nlstr = ShellString('\n'.join(self))
            return self.__nlstr

    n = nlstr = property(get_nlstr)

    def get_paths(self):
        from path import path
        try:
            return self.__paths
        except AttributeError:
            self.__paths = ShellList([path(p) for p in self if os.path.exists(p)])
            return self.__paths

    p = paths = property(get_paths)
