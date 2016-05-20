from ..core import Task


class match(Task):
    """
    Filters only matching files.

    NOTE: Matching is done from the right.
    """

    def __init__(self, pattern):
        self.pattern = pattern

    def process(self, inputs):
        for t, c, m in inputs:
            if t.match(self.pattern):
                yield t, c, m


class exclude(Task):
    """
    Excludes matching files.

    NOTE: Matching is done from the right.
    """

    def __init__(self, pattern):
        self.pattern = pattern

    def process(self, inputs):
        for t, c, m in inputs:
            if not t.match(self.pattern):
                yield t, c, m
