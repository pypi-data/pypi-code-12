from twisted.web.template import Element, renderer
from twisted.web.resource import Resource
from twisted.web.template import flatten
from twisted.web.template import XMLString
from twisted.web.server import NOT_DONE_YET
import pkg_resources
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

from py3o.fusion.template import tloader


class FeaturesElement(Element):

    cssurls = [
        "/static/bootstrap/css/bootstrap.min.css",
        "/static/css/pygments.css",
    ]

    loader = tloader('features.xml')
    header_loader = tloader('header.xml')
    scripts_loader = tloader('scripts.xml')

    odt2pdf_s = open(
        pkg_resources.resource_filename(
            'py3o.fusion',
            'static/examples/odt2pdf.py',
        ),
        'rb'
    ).read()

    fusion2pdf_s = open(
        pkg_resources.resource_filename(
            'py3o.fusion',
            'static/examples/fusion2pdf.py',
        ),
        'rb'
    ).read()

    @renderer
    def odt2pdf(self, request, tag):
        hcode = highlight(
            self.odt2pdf_s,
            PythonLexer(),
            HtmlFormatter(encoding='utf-8'),
        )
        return XMLString(hcode).load()

    @renderer
    def fusion2pdf(self, request, tag):
        hcode = highlight(
            self.fusion2pdf_s,
            PythonLexer(),
            HtmlFormatter(encoding='utf-8'),
        )
        return XMLString(hcode).load()

    @renderer
    def csslinks(self, request, tag):
        for cssurl in self.cssurls:
            yield tag.clone().fillSlots(cssurl=cssurl)

    @renderer
    def scripts(self, request, tag):
        return self.scripts_loader.load()

    @renderer
    def header(self, request, tag):
        return self.header_loader.load()

    @renderer
    def title(self, request, tag):
        return tag('py3o.fusion features')


class FeaturesPage(Resource):

    def flattened(self, output, request):
        # output should be None and ignored because flatten is as streamed data
        # to the connection as soon as it could
        #request.write('<!-- End of flow -->')
        request.finish()

    def render_GET(self, request):
        request.write('<!DOCTYPE html>\n')
        d = flatten(request, FeaturesElement(), request.write)
        d.addCallback(self.flattened, request)
        return NOT_DONE_YET
