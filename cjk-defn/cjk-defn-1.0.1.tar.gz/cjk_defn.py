#!/usr/bin/env python3
#
# Copyright (c) 2015-2016 Lapis Lazuli Texts
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Program module for a console CJK dictionary."""


import getopt
import io
import os
import signal
import sqlite3
import sys
import textwrap
import unicodedata

try:
    import readline
except ImportError:
    pass


USAGE = """Usage: cjk-defn [options] [dictionaries]

Look up dictionary definitions for CJK text.

Options:
  -h, --help          show this help message and exit
  -i, --info=DICT     show more information about a dictionary
  -v, --verbose       include information useful for debugging

Dictionaries:
%DICT_LIST
Variables:
   CJK_DEFN_DICTS     dictionaries to use by default

"""

CJK_UNICODE_RANGES = [
    (0x1100, 0x11FF),    # Hangul
    (0x2E80, 0x2FDF),    # CJK radicals
    (0x2FF0, 0x9FFF),    # CJK
    (0xA960, 0xA97F),    # Hangul
    (0xAC00, 0xD7FF),    # Hangul
    (0xFF00, 0xFFEF)]    # Halfwidth & fullwidth forms


def set_stdio_utf8():
    """
    Set standard I/O streams to UTF-8.

    Attempt to reassign standard I/O streams to new streams using UTF-8.
    Standard input should discard any leading BOM. If an error is raised,
    assume the environment is inflexible but correct (IDLE).

    """
    try:
        sys.stdin = io.TextIOWrapper(
            sys.stdin.detach(), encoding='utf-8-sig', line_buffering=True)
        sys.stdout = io.TextIOWrapper(
            sys.stdout.detach(), encoding='utf-8', line_buffering=True)
        sys.stderr = io.TextIOWrapper(
            sys.stderr.detach(), encoding='utf-8', line_buffering=True)
    except io.UnsupportedOperation:
        pass


def local_path(path=''):
    """
    Find a path relative to the module installation base directory.

    This function first looks for the given relative path in the same
    directory as the module. If the path does not exist there, then the
    function will try to find the base installation directory for the
    module, and join the path to that. This allows you to easily locate
    data files belonging to the module.

    """
    my_dir = os.path.abspath(os.path.dirname(__file__))
    if os.path.exists(os.path.join(my_dir, path)):
        return os.path.join(my_dir, path)
    while len(my_dir) > 3:
        my_dir, subdir = os.path.split(my_dir)
        if subdir == 'lib' or subdir == 'Lib':
            return os.path.join(my_dir, path)
    raise FileNotFoundError("Cannot find path to: '%s'" % (path))


def has_some_cjk(unicode_str):
    """Determine if any characters in a string are CJK characters."""
    for char in unicode_str:
        for range_start, range_end in CJK_UNICODE_RANGES:
            if ord(char) >= range_start and ord(char) <= range_end:
                return True
    return False


def strip_cjk_line(line):
    """Cut out spaces and other unnecessary characters."""
    if '║' in line:
        return line.split('║')[-1].strip()
    return line.strip()


def db_connect():
    """Return a new SQLite connection to the dictionary database."""
    rel_path = os.path.join('var', 'lib', 'cjk-defn', 'main.sqlite')
    return sqlite3.connect(local_path(rel_path))


def query_dict_basics(database):
    """Return details for a given dictionary."""
    dictionaries = {}
    curs = database.cursor()
    curs.execute('''
        SELECT DI_DICT, DI_SIGIL_S, DI_SIGIL_C, DI_SHORT_DESCR
        FROM DICTIONARIES
        ORDER BY DI_DICT ASC
        ''')
    for rec in curs:
        dictionaries[rec[0]] = rec
    curs.close()
    return dictionaries


def query_long_descr(database, dict_name):
    """Return long description for a given dictionary."""
    curs = database.cursor()
    sql = '''
        SELECT DI_LONG_DESCR
        FROM DICTIONARIES
        WHERE DI_DICT=?
        '''
    curs.execute(sql, (dict_name,))
    results = list(curs)
    if len(results) == 0:
        return None
    return results[0][0]


def query_definitions(database, dict_name, term):
    """Search the database for a dictionary definition."""
    definitions = []
    curs = database.cursor()
    sql = '''
        SELECT DF_ALT, DF_DEFN
        FROM DEFINITIONS
        WHERE DF_DICT=? AND DF_FORM1=? OR DF_DICT=? AND DF_FORM2=?
        '''
    curs.execute(sql, (dict_name, term, dict_name, term,))
    for alt_form, definition in curs:
        definitions.append([term, alt_form, definition])
    curs.close()
    return definitions


def get_char_defs(database, dict_name, line):
    """Return all definitions for each character."""
    defs = []
    for char in line:
        if has_some_cjk(char):
            result = query_definitions(database, dict_name, char)
            if len(result) > 0:
                defs += result
            else:
                defs += [char]
    return defs


def get_std_defs(database, dict_name, line):
    """Find dictionary definitions for any terms or phrases in a line."""
    results = []
    while len(line) > 0:
        query = line[:20]
        line = line[20:]
        while True:
            if not has_some_cjk(query):
                break
            entries = query_definitions(database, dict_name, query)
            if len(entries) > 0:
                results += entries
                break
            elif len(query) == 1:
                results += [query]
                break
            line = query[-1] + line
            query = query[:-1]
    return results


def print_defs(database, dict_name, is_char_dict, sigil, line):
    """Print relevant dictionary definitions for the line."""
    if is_char_dict:
        defs = get_char_defs(database, dict_name, line)
    else:
        defs = get_std_defs(database, dict_name, line)
    for defn in defs:
        if len(defn) == 1:
            print('  %s| %s' % (sigil, defn[0]))
        else:
            line = '  %s| %s (%s): %s' % (sigil, defn[0], defn[1], defn[2])
            indent = '  ' + sigil + '|            '
            print(textwrap.fill(line, width=66, subsequent_indent=indent))
    if len(defs) > 0:
        print()


def print_input_defs(user_selection):
    """Print definitions for all stdin text, using the given dictionaries."""
    database = db_connect()
    try:
        chosen = []
        dict_info = query_dict_basics(database)
        for dict_name in user_selection:
            if dict_name.endswith('/c') and dict_name[:-2] in dict_info:
                real_name = dict_name[:-2]
                sigil = dict_info[real_name][2]
                chosen.append([real_name, True, sigil])
            elif dict_name in dict_info:
                sigil = dict_info[dict_name][1]
                chosen.append([dict_name, False, sigil])
            else:
                raise ValueError('dictionary not found: ' + dict_name)
        line_number = 1
        while True:
            line = strip_cjk_line(unicodedata.normalize('NFC', input()))
            print('[%d] %s\n' % (line_number, line))
            if line != '':
                for dict_name, is_char_dict, sigil in chosen:
                    print_defs(database, dict_name, is_char_dict, sigil, line)
            line_number += 1
    except EOFError:
        return 0
    finally:
        database.close()
    return 0


def long_descr(dict_name):
    try:
        database = db_connect()
        info = query_long_descr(database, dict_name)
        if not info:
            return 'Nothing found.\n'
        new_s = '\n'
        for line in info.split('\n'):
            if line.strip() == '':
                pass
            if len(line) < 80:
                new_s += line + '\n'
            else:
                new_s += textwrap.fill(line, width=79) + '\n'
        return new_s
    except sqlite3.OperationalError:
        raise


def usage():
    """Show usage information including a listing of dictionaries."""
    try:
        database = db_connect()
        db_listing = ''
        try:
            dict_info = query_dict_basics(database)
            for row in sorted(dict_info.values()):
                db_listing += '   %-11s %2s %2s  %-57s\n' % row
            msg = USAGE.replace('%DICT_LIST', db_listing)
        finally:
            database.close()
    except sqlite3.OperationalError:
        msg = USAGE.replace('%DICT_LIST', '\nCannot connect to database!\n')
    return msg


def main(argv):
    """Run as a portable command-line program."""
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    set_stdio_utf8()
    verbose = False
    try:
        opts, args = getopt.getopt(
            argv[1:], 'hvi:', ['help', 'verbose', 'info'])
        for option, arg in opts:
            if option in ('-h', '--help'):
                print(usage(), end='')
                return 0
            if option in ('-v', '--verbose'):
                verbose = True
            if option in ('-i', '--info'):
                print(long_descr(arg), end='')
                return 0
        selection = []
        if len(args) > 0:
            for dict_name in args:
                selection.append(dict_name)
        else:
            if os.getenv('CJK_DEFN_DICTS'):
                for dict_name in os.getenv('CJK_DEFN_DICTS').split():
                    selection.append(dict_name.strip())
            else:
                sys.stderr.write(usage())
                return 1
        print_input_defs(selection)
        return 0
    except KeyboardInterrupt:
        return 1
    except Exception as err:
        if verbose:
            raise
        else:
            sys.stderr.write('cjk-defn: ' + str(err) + '\n')
            return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
