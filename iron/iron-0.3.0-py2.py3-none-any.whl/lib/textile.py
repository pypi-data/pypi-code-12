from ..core import Task


class textile(Task):
    """Converts Textile to HTML."""

    def __init__(self):
        try:
            from textile import textile as textile_fn
        except ImportError as e:
            raise ImportError('To use textile(), run: pip install textile') from e

        self.convert = textile_fn

    def lazy_convert(self, contents):
        yield self.convert(b''.join(contents).decode('utf-8')).encode('utf-8')

    def process(self, inputs):
        for t, c, m in inputs:
            t2 = t.with_suffix('.html')
            yield t2, self.lazy_convert(c), m
