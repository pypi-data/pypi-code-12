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
HEADER_DELIM = b'\n'
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

        hash_cnf(v for v in [3, 2, 1, -3, 0, -1, 2, 0])
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
            sha1.update(str(nbvars).encode(ENCODING))
            sha1.update(LITERAL_DELIM)
        elif i == 1:
            nbclauses = lit
            clause_ended = False
            if nbclauses <= 0:
                tmpl = "nbclauses must be non-negative, is {}".format(lit)
                raise ValueError(tmpl)
            sha1.update(str(nbvars).encode(ENCODING))
            sha1.update(LITERAL_DELIM)
            sha1.update(HEADER_DELIM)
        elif lit == 0:
            if clause_ended:
                continue  # multiple zeros truncated to a single one
            clauses += 1
            sha1.update(CLAUSE_DELIM)
            clause_ended = True
        else:
            clause_ended = False
            if not (-nbvars <= lit <= nbvars):
                tmpl = "Variable {} outside range {}--{}".format(lit, 1, nbvars)
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


class BlockwiseReader:
    """A reader which takes blocks of bytes from a given stream and
    returns bytes individually
    """

    def __init__(self, stream, eof_symbol=None):
        self.stream = stream

        self.index = 0
        self.block = b''
        self.eof_symbol = eof_symbol
        self.eof = False

        self.read_next_block()

    def read_next_block(self):
        if self.eof:
            return
        try:
            self.block = next(self.stream)
            self.index = 0
        except StopIteration:
            self.eof = True

    def advance(self):
        self.index += 1
        if self.index >= len(self.block):
            self.read_next_block()

    def peek(self):
        if self.eof:
            return self.eof_symbol
        return bytes([self.block[self.index]])


class Consumer:
    """A consumer for bytes to simplify bytes parsing.
    It takes byte from the BlockwiseReader and allows
    to skip and expect/consume bytes.
    """

    WS = string.whitespace.encode(ENCODING)
    LINE_WS = bytes(string.whitespace.replace('\n', '').encode(ENCODING))
    NEWLINE = os.linesep.encode(ENCODING)
    EOF = b'\0'

    def __init__(self, stream):
        self.reader = BlockwiseReader(stream, eof_symbol=self.EOF)
        self.lineno = 1

    def __str__(self):
        return "Consume(current_byte={})".format(repr(self.reader.peek()))

    def __next__(self):
        value = self.reader.peek()
        if value == self.NEWLINE:
            self.lineno += 1
        self.reader.advance()
        return value

    def peek(self):
        return self.reader.peek()

    # skip bytes, independent whether they are given or not

    def skip(self, skip_bytes):
        given_byte = self.peek()
        while given_byte in skip_bytes:
            next(self)
            given_byte = self.peek()

    # expect some byte, otherwise error

    def byte_error(self, byte, exp):
        errmsg = "Invalid byte {} at line {}, expected {}"
        return DimacsSyntaxError(errmsg.format(byte, self.lineno, exp))

    def consume(self, expected_bytes, expected_bytes_description):
        given_byte = next(self)
        if given_byte == self.EOF:
            errmsg = "Unexpected end of file at line {}"
            raise DimacsSyntaxError(errmsg.format(self.lineno))
        if given_byte not in expected_bytes:
            raise self.byte_error(given_byte, expected_bytes_description)
        else:
            return given_byte

    # high-level values

    def consume_line_whitespace(self):
        self.consume(self.LINE_WS, 'whitespace')
        self.skip(self.LINE_WS)

    def consume_whitespace(self):
        self.consume(self.WS, 'whitespace')
        self.skip(self.WS)

    def consume_integer(self, positive=False):
        digits = string.digits.encode(ENCODING)
        if positive:
            val = self.consume(digits, 'digit')
        else:
            val = self.consume(b'-' + digits, 'hyphen or digit')
        while self.peek() in digits:
            val += self.consume(digits, 'digit')
        return int(val.decode(ENCODING))

    def skip_line_whitespace(self):
        self.skip(self.LINE_WS)

    def skip_whitespace(self):
        self.skip(self.WS)

    def skip_line(self):
        while self.peek() != self.NEWLINE:
            next(self)
        next(self)

    def skip_newline(self):
        if self.peek() == self.NEWLINE:
            next(self)
            return True
        return False



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
    value_cache = ""
    consumer = Consumer(dimacs_bytes)

    # read header
    while consumer.peek() in ignore_lines:
        consumer.skip_line()
    consumer.consume(b'p', "keyword 'p'")
    consumer.consume_whitespace()
    consumer.consume(b'c', "keyword 'cnf'")
    consumer.consume(b'n', "keyword 'cnf'")
    consumer.consume(b'f', "keyword 'cnf'")
    consumer.consume_whitespace()
    yield consumer.consume_integer(positive=True)
    consumer.consume_whitespace()
    yield consumer.consume_integer(positive=True)
    consumer.consume_whitespace()

    # read clauses
    while consumer.peek() != b'\0':
        while consumer.peek() in ignore_lines:
            consumer.skip_line()
        consumer.skip_line_whitespace()
        while True:
            yield consumer.consume_integer()
            consumer.skip_line_whitespace()
            if consumer.skip_newline():
                consumer.skip_line_whitespace()
                break
