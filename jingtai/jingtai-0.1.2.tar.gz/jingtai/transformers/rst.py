from docutils.core import publish_parts
from mako.template import Template

from .base import register_transformer
from .page import PageTransformer
from .util import split_markup


@register_transformer
class ReStructuredTextTransformer(PageTransformer):
    input_ext = '.rst'

    def transform(self, src):
        ctx, text = split_markup(src.read_text())
        ctx['BASE'] = self.site.base_url
        text = '<%inherit file="base.plim" />\n\n' + self.to_html(text)
        tmpl = Template(
            text=text,
            lookup=self.lookup)
        return tmpl.render(**ctx)

    def to_html(self, text):
        result = publish_parts(
            text,
            writer_name='html',
            settings_overrides={'initial_header_level': 2})['html_body']
        # Get rid of the outer div.
        return result[22:-7]
