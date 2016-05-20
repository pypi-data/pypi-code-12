from ..core import Task


class minify_html(Task):
    """Minifies HTML input files."""

    def __init__(self, *htmlmin_args, **htmlmin_kwargs):
        try:
            from htmlmin import Minifier
        except ImportError as e:
            raise ImportError('To use minify_html(), run: pip install htmlmin') from e

        self.minifier = Minifier(*htmlmin_args, **htmlmin_kwargs)

    def lazy_minify(self, contents):
        yield self.minifier.minify(b''.join(contents).decode('utf-8')).encode('utf-8')

    def process(self, inputs):
        for t, c, m in inputs:
            yield t, self.lazy_minify(c), m
