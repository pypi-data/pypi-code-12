from functools import partial

from ..core import Task


class markdown(Task):
    """Converts Markdown to HTML."""

    def __init__(self):
        try:
            from markdown import markdown as markdown_fn
        except ImportError as e:
            raise ImportError('To use markdown(), run: pip install markdown') from e

        from markdown.extensions.codehilite import CodeHiliteExtension
        hilite = CodeHiliteExtension(guess_lang=False)

        self.convert = partial(markdown_fn, extensions=[
            # 'markdown.extensions.codehilite',
            hilite,
            'markdown.extensions.fenced_code',
            'markdown.extensions.attr_list',
            'markdown.extensions.sane_lists',
            # 'markdown.extensions.tables',
            'markdown.extensions.headerid',
            'markdown.extensions.def_list',
        ])

    def lazy_convert(self, contents):
        yield self.convert(b''.join(contents).decode('utf-8')).encode('utf-8')

    def process(self, inputs):
        for t, c, m in inputs:
            t2 = t.with_suffix('.html')
            yield t2, self.lazy_convert(c), m
