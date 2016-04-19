#!python
#
# This file is part of https://github.com/zsquareplusc/python-embedded-launcher
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
Extract the launcher.exe.
"""
import argparse
import os
import pkgutil
import sys


def copy_launcher(fileobj, use_py2=False, use_64bits=False):
    """copy raw launcher exe to given file object"""
    if use_py2:
        filename = 'launcher27.exe'
        if use_64bits:
            raise ValueError('64 bit support for Python 2.7 currently not implemented')
    else:
        if use_64bits:
            filename = 'launcher3-64.exe'
        else:
            filename = 'launcher3-32.exe'
    fileobj.write(pkgutil.get_data(__name__, filename))


def main():
    """Command line tool entry point"""
    parser = argparse.ArgumentParser(description='copy the launcher.exe')

    group_out = parser.add_argument_group('output options')
    group_out.add_argument('-o', '--output', metavar='FILE',
                           help='write to this file')

    group_bits = parser.add_argument_group('architecture', 'default value is based on sys.executable')
    group_bits_choice = group_bits.add_mutually_exclusive_group()
    group_bits_choice.add_argument('--32', dest='bits32', action='store_true', default=False,
                                   help='force copy of 32 bit version')
    group_bits_choice.add_argument('--64', dest='bits64', action='store_true', default=False,
                                   help='force copy of 64 bit version')

    group_pyver = parser.add_argument_group('launcher Python version', 'default value is based on sys.executable')
    group_pyver_choice = group_pyver.add_mutually_exclusive_group()
    group_pyver_choice.add_argument('-2', dest='py2', action='store_true', default=False,
                                    help='force use of Python 2.7 launcher')
    group_pyver_choice.add_argument('-3', dest='py3', action='store_true', default=False,
                                    help='force use of Python 3.x launcher')

    args = parser.parse_args()

    use_python27 = False
    if (sys.version_info.major == 2 and not args.py3) or args.py2:
        use_python27 = True

    is_64bits = sys.maxsize > 2**32  # recommended by docs.python.org "platform" module
    if args.bits64:
        use_64bits = True
    elif args.bits32:
        use_64bits = False
    elif is_64bits:
        use_64bits = True
    else:
        use_64bits = False
    dest_dir = os.path.dirname(args.output)
    if dest_dir and not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    with open(args.output, 'wb') as exe:
        copy_launcher(exe, use_python27, use_64bits)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
    main()
