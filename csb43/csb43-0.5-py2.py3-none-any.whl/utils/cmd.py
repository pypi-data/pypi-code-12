#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
.. note::

    license: GNU Lesser General Public License v3.0 (see LICENSE)

Convert a **CSB/AEB norm 43** file to other file formats.

Supported formats:

- `OFX <http://www.ofx.net/>`_
- `HomeBank CSV <http://homebank.free.fr/help/06csvformat.html>`_
- *HTML*
- *JSON*
- *ODS*: OpenDocument spreadsheet
- *CSV*, *TSV*: comma- or tab- separated values
- *XLS*: Microsoft Excel spreadsheet
- *XLSX*: OOXML spreadsheet
- *YAML*

Options:
-----------

::

    usage: csb2format [-h] [-s] [-df] [-d DECIMAL]
                  [-f {csv,homebank,html,json,ods,ofx,tsv,xls,xlsx,yaml}] [-v]
                  csbFile convertedFile

    Convert a CSB43 file to another format

    positional arguments:
    csbFile               a csb43 file ('-' for stdin)
    convertedFile         destination file ('-' for stdout)

    optional arguments:
    -h, --help            show this help message and exit
    -s, --strict          strict mode
    -df, --dayfirst       use DDMMYY as date format while parsing the csb43
                          file instead of YYMMDD
    -d DECIMAL, --decimal DECIMAL
                          set the number of decimal places for the currency
                          type (default: 2)
    -f {csv,homebank,html,json,ods,ofx,ofx1,tsv,xls,xlsx,yaml}, --format \
{csv,homebank,html,json,ods,ofx,ofx1,tsv,xls,xlsx,yaml}
                            Format of the output file. Default: ofx

Examples
----------

- Converting to OFX format:

    ::

        $ csb2format transactions.csb transactions.ofx

        $ csb2format --format ofx transactions.csb transactions.ofx

    or

    ::

        $ csb2format transactions.csb - > transactions.ofx

    From another app to file

    ::

        $ get_my_CSB_transactions | csb2format - transactions.ofx

- Converting to XLSX spreadsheet format:

    ::

        $ csb2format --format xlsx transactions.csb transactions.xlsx

Spreadsheets
-------------

*ODS* and *XLS* files are generated as books, with the first sheet containing
the accounts information, and the subsequent sheets containing the transactions
of each one of the accounts.

'''

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from .. import __version__
from .compat import m3_unicode, m3_bytes
from . import DECIMAL, Csb43Exception
from .. import csb43 as csb_43, formats as sheet, homebank, ofx
from ..i18n import tr as _

import codecs
import argparse
import sys

_FORMATS = sorted(list(set(['ofx', 'ofx1', 'homebank'] + sheet.FORMATS)))

_DEFAULT_FORMAT = "ofx" if "ofx" in _FORMATS else _FORMATS[0]


class FileTypeE(object):
    """Factory for creating file object types
    Instances of FileType are typically passed as type= arguments to the
    ArgumentParser add_argument() method.
    Keyword Arguments:
        - mode -- A string indicating how the file is to be opened. Accepts the
            same values as the builtin open() function.
        - bufsize -- The file's desired buffer size. Accepts the same values as
            the builtin open() function.
        - encoding -- Character encoding which should be used for the open \
        codec.
    """

    def __init__(self, mode='r', bufsize=-1, encoding='utf-8'):
        self._mode = mode
        self._bufsize = bufsize
        self._encoding = encoding

    def __call__(self, filename):
        # the special argument "-" means sys.std{in,out}
        if filename == '-':
            if 'r' in self._mode:
                return sys.stdin
            elif 'w' in self._mode:
                return sys.stdout
            else:
                msg = _('argument "-" with mode %r') % self._mode
                raise ValueError(msg)

        # all other arguments are used as file names
        try:
            if "b" in self._mode:
                return open(
                    filename,
                    mode=self._mode,
                    buffering=self._bufsize
                )
            return codecs.open(
                filename,
                mode=self._mode,
                encoding=self._encoding,
                buffering=self._bufsize
            )
        except IOError as e:
            message = _("can't open '%s': %s")
            raise argparse.ArgumentTypeError(message % (filename, e))

    def __repr__(self):
        args = self._mode, self._bufsize
        args_str = ', '.join(repr(arg) for arg in args if arg != -1)
        return '%s(%s)' % (type(self).__name__, args_str)


def get_parser():
    parser = argparse.ArgumentParser(description=_(
        "Convert a CSB43 file to "
        "another format"))

    group1 = parser.add_argument_group("csb43 arguments")
    group1.add_argument(
        'csbFile',
        type=FileTypeE('rU', encoding='latin-1'),
        help=_("a csb43 file ('-' for stdin)")
    )
    group1.add_argument(
        '-s', '--strict', dest='strict', action='store_true',
        default=False,
        help=_('strict mode (default: %(default)s)')
    )
    group1.add_argument(
        '-df', '--dayfirst', dest="yearFirst",
        action='store_false', default=True,
        help=_(
            "use DDMMYY as date format while parsing the"
            " csb43 file instead of YYMMDD"
            " (default: %(default)s)"
        )
    )
    group1.add_argument(
        '-d', '--decimal', dest="decimal", type=int,
        default=DECIMAL,
        help=_(
            "set the number of decimal places for the"
            " currency type (default: %(default)d)"
        )
    )
    group1.add_argument(
        '-V', '--verbose', dest="silent",
        action='store_false',
        default=True,
        help=_("show csb43 warnings")
    )

    group2 = parser.add_argument_group("output arguments")
    group2.add_argument(
        'convertedFile',
        type=str,
        help=_("destination file ('-' for stdout)")
    )
    group2.add_argument(
        '-f', '--format', dest="format", type=str,
        choices=_FORMATS,
        default=_DEFAULT_FORMAT,
        help=_(
            "Format of the output file"
            " (default: %(default)s)"
        )
    )

    parser.add_argument(
        '-v', '--version', dest="version",
        action='version',
        version='%(prog)s ' + __version__
    )

    return parser


def convert(args):
    csb = csb_43.File(
        args.csbFile,
        strict=args.strict,
        decimal=args.decimal,
        yearFirst=args.yearFirst,
        silent=args.silent
    )

    print("*", _("File:"), args.csbFile.name, file=sys.stderr)

    aFormat = args.format.lower()

    csb.showInfo(sys.stderr)

    outFile = FileTypeE("w", encoding="utf-8")

    # OFX format
    if aFormat in ('ofx', 'ofx1'):
        data = ofx.convertFromCsb(csb, sgml=(aFormat == 'ofx1'))

        with outFile(args.convertedFile) as fd:
            fd.write(m3_unicode(data))
    # Homebank csv format
    elif aFormat == 'homebank':
        with outFile(args.convertedFile) as fd:
            for record in homebank.convertFromCsb(csb):
                fd.write(m3_unicode(record))
                fd.write('\n')
    # Dict and tabular formats
    else:
        data = sheet.convertFromCsb(csb, aFormat)

        content = getattr(data, aFormat)

        if isinstance(content, m3_bytes):
            outFile = FileTypeE("wb")

        with outFile(args.convertedFile) as fd:
            fd.write(content)
    try:
        args.csbFile.close()
    except:
        pass


def main():
    try:
        args = get_parser().parse_args()

        convert(args)

    except Csb43Exception as e:
        print(str(e), file=sys.stderr)
        return 1

    return 0
