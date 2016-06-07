"""
Usage:
    python -m docpie.complete [options] --exec=<file_name>   [--pie=<pie_name>]
    python -m docpie.complete [options] --import=<file_name> [--pie=<pie_name>]
    python -m docpie.complete [options] <executable_name> [<input>] [<output>]
    python -m docpie.complete --example=<sth>
    python -m docpie.complete command
    python -m docpie.complete <args>

Options:
    --version                  print the version of this tool
    -v, --verbose              print more message (for debug)
    -h, --help                 print this screen

Exec Options:
    -e, --exec=<file_name>

    <input>        the input file which contains the help message
                   that you pass to docpie. Use ``-`` for stand input
                   [default: -]
    <output>       the output file to write the tab-complete bash script.
                   You may want to set it to
                   ``/etc/bash_completion.d/<your-script-name>.sh``, then
                   use ``. /etc/bash_completion.d/<your-script-name>.sh``
                   to make this tab-complete works. Use ``-`` for stand output
                   [default: -]
"""
import re
import logging
import sys
from docpie.error import DocpieError
try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest

if sys.version_info[0] < 3:
    import codecs

    def open(file, mode='r', buffering=-1, encoding=None,
             errors=None, newline=None, closefd=True, opener=None):
        return codecs.open(filename=file, mode=mode, encoding=encoding,
                           errors=errors, buffering=buffering)


__version__ = '0.0.1'
logger = logging.getLogger('docpie.complete')


def complete(pie, name=None):
    # name = name or pie.name
    # if not name:
    #     raise DocpieError('You must specify executable program name')
    # safe_name = safe_func_name(name)
    # usages = pie.usages
    # levels = []
    #
    # # print(usages[0][0].options)
    # pie.preview()
    # for level, instance in enumerate(zip_longest(*usages)):
    #     print(level, *instance, sep=', ')
    pass


SAFE_FUNC_NAME = re.compile(r'[^a-zA-Z0-9_]')


def safe_func_name(name):
    return SAFE_FUNC_NAME.sub('_', name)

# def _parse_args(args):
#
#
# def main(args):
#     if args['--verbose']:
#         bashlog.stdoutlogger(logger, bashlog.DEBUG)
#
#
#
#     in_file = args['<input>']
#     out_file = args['<output>']
#     prog_name = args['--name']
#     in_and_out = []
#
#     if in_file in (None, '-'):
#         help_msg = sys.stdin.read()
#     else:
#         with open(in_file, 'r', encoding='utf-8') as f:
#             help_msg = f.read()
#
#     if out_file in (None, '-'):
#         need_close = False
#         out_io = sys.stdout
#     else:
#         out_io = open(out_file, 'r', encoding='utf-8')
#         need_close = True
#
#     write = out_io.write
#     result =

if __name__ == '__main__':
    from docpie import docpie, bashlog, Docpie
    # args = docpie(__doc__, version=__version__, name='docpie.complete')
    complete(Docpie(__doc__, version=__version__, name='docpie.complete'))
    # main(args)