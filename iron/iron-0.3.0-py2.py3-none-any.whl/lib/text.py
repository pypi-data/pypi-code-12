import re
from itertools import chain

from more_itertools import flatten
from pathlib import Path

from ..core import Task
from ._helpers import as_byte_stream, as_text


class concat(Task):
    """
    Concatenates input stream contents to the given output file, in the order
    that they appear in the inputs.

    Modifies target filename.
    Modifies stream contents.
    Destroys metadata.

    Example::

        foo.js, bar.js, qux.js  =>  all.js

    """
    def __init__(self, dest):
        self.dest = Path(dest)

    def process(self, inputs):
        yield self.dest, flatten(chain(c for _, c, _ in inputs)), {}


class contents_replace(Task):
    def __init__(self, substring, replacement):
        self.substring = substring
        self.replacement = replacement

    def lazy_replace(self, c):
        contents = b''.join(c).decode('utf-8').replace(self.substring, self.replacement).encode('utf-8')
        yield contents

    def process(self, inputs):
        for t, c, m in inputs:
            yield t, self.lazy_replace(c), m


class footer(Task):
    def __init__(self, bites):

        if isinstance(bites, str):
            bites = bites.encode('utf-8')
        if not isinstance(bites, bytes):
            raise TypeError('expected bytes')
        self.bites = bites

    def process(self, inputs):
        for t, c, m in inputs:
            yield t, chain(c, [self.bites]), m


class header(Task):
    def __init__(self, bites):

        if isinstance(bites, str):
            bites = bites.encode('utf-8')
        if not isinstance(bites, bytes):
            raise TypeError('expected bytes')
        self.bites = bites

    def process(self, inputs):
        for t, c, m in inputs:
            yield t, chain([self.bites], c), m


class regex(Task):
    """
    Takes a `pattern` (can be a compiled regex), and a `replacement`, and will
    perform the replacement on the contents of each input.

    Note: if you pass in the pattern as a string, then `re.MULTILINE` is
    assumed, since the contents of the file is passed to `.sub()` as a single
    string, not line-by-line.  If you don't want this, override the `flags`
    argument.

    Note: the `flags` argument is ignored when you pass in a pre-compiled
    regex.
    """
    def __init__(self, pattern, replacement, *, flags=re.MULTILINE):
        if isinstance(pattern, str):
            self.regex = re.compile(pattern, flags)
        elif hasattr(pattern, 'sub'):  # quacks like a compiled regexp
            self.regex = pattern
        else:
            raise TypeError('Expected a compiled regexp or a pattern, but got {}'.format(pattern))
        self.replacement = replacement

    def process(self, inputs):
        for t, c, m in inputs:
            contents = as_text(c)
            c2 = self.regex.sub(self.replacement, contents)
            yield t, as_byte_stream(c2), m
