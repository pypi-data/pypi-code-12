#!/usr/bin/env python3

"""
    cnfhash.hashing
    ---------------

    Integer hashing library for cnfhash.

    (C) Lukas Prokop, 2015, Public Domain
"""

import os
import string
import hashlib
import functools

LITERAL_DELIM = b' '
CLAUSE_DELIM = b'0\n'
ENCODING = 'ascii'


def hash_cnf(ints: [int]):
    """Hash a given CNF defined as sequence of integers.

    `ints` is a sequence of integers:
    (1) the first 2 integers are expected to be nbvars and nbclauses
    (2) the following integers are considered literals
        where 0 terminates a clause

    Hence, the following file::

        p cnf 3 2
        1 -3 0
        -1 2 0

    will be hashed correctly by calling::

        hash_cnf([3, 2, 1, -3, 0, -1, 2, 0])
    """
    sha1 = hashlib.sha1()
    clause_ended = False
    nbclauses = None
    clauses = 0

    sha1.update(b"p cnf ")

    for i, lit in enumerate(ints):
        if i == 0:
            nbvars = lit
            clause_ended = False
            if nbvars <= 0:
                tmpl = "nbvars must be non-negative, is {}".format(lit)
                raise ValueError(tmpl)
        elif i == 1:
            nbclauses = lit
            clause_ended = False
            if nbclauses <= 0:
                tmpl = "nbclauses must be non-negative, is {}".format(lit)
                raise ValueError(tmpl)
        elif lit == 0:
            if clause_ended:
                continue  # multiple zeros truncated to a single one
            clauses += 1
            sha1.update(CLAUSE_DELIM)
            clause_ended = True
        else:
            clause_ended = False
            if not (-nbvars <= lit <= nbvars):
                tmpl = "Variable {} outside range ({})--({})".format(lit, -nbvars, nbvars)
                raise ValueError(tmpl)
            sha1.update(str(lit).encode(ENCODING))
            sha1.update(LITERAL_DELIM)

    if nbclauses is None:
        errmsg = "Premature end, CNF must at least contain header values"
        raise ValueError(errmsg)
    if not clause_ended:
        raise ValueError("CNF must be terminated by zero")
    if nbclauses != clauses:
        tmpl = "Invalid number of clauses, expected {}, got {} clauses"
        raise ValueError(tmpl.format(nbclauses, clauses))

    return 'cnf1$' + sha1.hexdigest()


def hash_decorator(f):
    """Decorator wrapping `hash_cnf`"""
    @functools.wraps(f)
    def inner(*args, **kwargs):
        return hash_cnf(f(*args, **kwargs))
    return inner


class DimacsSyntaxError(Exception):
    """An exception representing a syntax error in DIMACS"""
    pass


@hash_decorator
def hash_dimacs(dimacs_bytes, ignore_lines=b'c%'):
    """Given a DIMACS file as sequence of bytes,
    return the corresponding cnfhash.

    `dimacs_bytes`
      A sequence of byte specifying content in DIMACS format.
    `ignore_lines`
      A sequence of characters. If a line starts with this
      character, the line is ignored. Example::

          ignore_lines=b'c'

      will ignore all lines like::

          c this is a comment
    """
    # '%' is included because ... there are strange CNF files out there
    skip_line = False
    got_newline = False
    got_line_whitespace = False
    start, end = 0, 0
    mode = 0
    lineno = 1
    intcache = ""

    WS = set(string.whitespace.encode(ENCODING))
    LINE_WS = set(string.whitespace.replace('\n', '').encode(ENCODING))
    DIGIT = set(string.digits.encode(ENCODING))
    HYPHEN = ord('-')
    NEWLINE = ord('\n')
    KEYWORD = b'pcnf'

    def unexp_byte(given, expected):
        errmsg = "Unexpected byte {} found at line {}, expected {}"
        return DimacsSyntaxError(errmsg.format(bytes([given]), lineno, expected))

    # I know this is a rdiciulously long state machine.
    # However, a consume-parser design was terribly slow
    while True:
        try:
            block = next(dimacs_bytes)
        except StopIteration:
            break

        for i in range(len(block)):
            if block[i] == NEWLINE:
                lineno += 1
            if skip_line:
                if block[i] == NEWLINE:
                    skip_line = False
                    got_newline = True
                continue

            if block[i] in LINE_WS:
                got_line_whitespace = True
            elif block[i] == NEWLINE:
                got_newline = True
            else:
                char = block[i]
                if mode == 0:
                    if char == ord(b'p'):
                        mode = 1
                    elif char in set(ignore_lines):
                        skip_line = True
                    else:
                        raise unexp_byte(char, "keyword 'p'")
                elif mode == 1:
                    if not got_line_whitespace:
                        raise unexp_byte(char, "whitespace")
                    elif char == ord(b'c'):
                        mode = 2
                    else:
                        raise unexp_byte(char, "keyword 'cnf'")
                elif mode == 2:
                    if not got_line_whitespace and char == ord(b'n'):
                        mode = 3
                    else:
                        raise unexp_byte(char, "keyword 'cnf'")
                elif mode == 3:
                    if not got_line_whitespace and char == ord(b'f'):
                        mode = 4
                    else:
                        raise unexp_byte(char, "keyword 'cnf'")
                elif mode == 4:
                    if got_line_whitespace and char in DIGIT:
                        intcache += chr(char)
                        mode = 5
                    else:
                        raise unexp_byte(char, "non-negative integer")
                elif mode == 5:
                    if not got_line_whitespace and char in DIGIT:
                        intcache += chr(char)
                    elif got_line_whitespace and char in DIGIT:
                        yield int(intcache)
                        intcache = chr(char)
                        mode = 6
                    else:
                        raise unexp_byte(char, "non-negative integer")
                elif mode == 6:
                    if got_line_whitespace or got_newline:
                        yield int(intcache)
                        if char in DIGIT or char == HYPHEN:
                            intcache = chr(char)
                        else:
                            intcache = ''
                            if got_newline and char in set(ignore_lines):
                                skip_line = True
                        mode = 7
                    elif not got_line_whitespace and char in DIGIT:
                        intcache += chr(char)
                    else:
                        raise unexp_byte(char, "non-negative integer")
                elif mode == 7:
                    if (got_line_whitespace or got_newline) and intcache:
                        yield int(intcache)
                        intcache = ''
                    if got_newline and char in set(ignore_lines):
                        skip_line = True
                    elif char in DIGIT or char == HYPHEN:
                        intcache += chr(char)
                    else:
                        raise unexp_byte(char, "digit or hyphen")

                got_line_whitespace = False
                got_newline = False

    if intcache:
        yield int(intcache)
