"""
Copyright 2016 Gu Zhengxiong <rectigu@gmail.com>

This file is part of IntDump.

IntDump is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

IntDump is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with IntDump.  If not, see <http://www.gnu.org/licenses/>.
"""


# TODO: Generalize to bindump instead of merely intdump.
# WARN: But do it when you are in need.
# INFO: Refer to the dumping functionality of IntelliCoder.


from __future__ import division, absolute_import, print_function
from pydoc import pager

import click

from . import PROGRAM_NAME, VERSION_PROMPT
from .interpreters import unpack_int


# Note on click.Choice.
# click.Choice([1,2,3,4,5]) is not allowed
# <https://github.com/pallets/click/issues/244>
# But what's the rationale?

UNPACK_FMT = {
    # signed False True
    '8': ('B', 'b'), '16': ('H', 'h'),
    '32': ('L', 'l'), '64': ('Q', 'q')
}

BASE = {
    '2': bin, '8': oct, '10': int, '16': hex
}


@click.command(
    context_settings=dict(help_option_names=['-h', '--help']))
@click.version_option(VERSION_PROMPT,
                      '-V', '--version', prog_name=PROGRAM_NAME)
@click.option('-w', '--width',
              type=click.Choice(sorted(UNPACK_FMT.keys(), key=int)),
              default='64', show_default=True,
              help='Specify the width of the integer in bits.')
@click.option('-s', '--signed', is_flag=True,
              help='Interpret as signed integers.')
@click.option('-B', '--big-endian', is_flag=True,
              help='Interpret as bit-endian integers.')
@click.option('-b', '--base',
              type=click.Choice(sorted(BASE.keys(), key=int)),
              default='16', show_default=True,
              help='Specify the base of output.')
@click.option('-a', '--array', is_flag=True,
              help='Output in array forms.')
@click.option('-p', '--use-pager', is_flag=True,
              help='Output using a pager.')
@click.argument('streams', nargs=-1, required=True,
                type=click.File('rb'), metavar='FILENAME ...')
def main(width, streams, signed, big_endian, base, array, use_pager):
    """Interpret binary file in some predefined manners
    that help.

    For the time being, we only interpret integers from binary files.
    """
    endianness = '>' if big_endian else '<'
    fmt = endianness + UNPACK_FMT[width][signed]
    for stream in streams:
        ints = unpack_int(stream, fmt, width, BASE[base])
        if array:
            delim = ', '
        else:
            delim = '\n'
        display = delim.join(str(one) for one in ints)
        func = pager if use_pager else print
        func(display)
