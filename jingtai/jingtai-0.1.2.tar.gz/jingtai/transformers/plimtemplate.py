import subprocess

from mako.template import Template
from plim import preprocessor

from .base import register_transformer
from .page import PageTransformer
from .util import split_markup


IMPORTS = [
    'from jingtai.assets import stylesheet, script'
]


@register_transformer
class PlimTransformer(PageTransformer):
    input_ext = '.plim'

    def transform(self, src):
        ctx, text = split_markup(src.read_text())
        ctx['BASE'] = self.site.base_url
        tmpl = Template(
            text=text,
            lookup=self.lookup,
            preprocessor=preprocessor,
            imports=IMPORTS)
        return tmpl.render(**ctx)
