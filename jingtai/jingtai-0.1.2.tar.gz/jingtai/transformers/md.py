import markdown2
from mako.template import Template

from .base import register_transformer
from .page import PageTransformer
from .util import split_markup


EXTRAS = ['fenced-code-blocks', 'footnotes']


@register_transformer
class MarkdownTransformer(PageTransformer):
    input_ext = '.md'

    def transform(self, src):
        ctx, text = split_markup(src.read_text())
        ctx['BASE'] = self.site.base_url
        text = '<%inherit file="base.plim" />\n\n' + self.to_html(text)
        # Note that we don't use the plim preprocessor here, because arbitrary
        # HTML confuses the plim parser.
        tmpl = Template(
            text=text,
            lookup=self.lookup)
        return tmpl.render(**ctx)

    def to_html(self, text):
        return markdown2.markdown(text, extras=EXTRAS)
