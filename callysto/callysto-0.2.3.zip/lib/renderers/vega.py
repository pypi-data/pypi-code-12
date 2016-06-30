"""
Graphics renderer for Vega and Vega-lite grammars of graphic; see
http://vega.github.io/vega/ and http://vega.github.io/vega-lite/

"""

__all__ = (
    "VegaRenderer",)

import json
import logging
import uuid

import core.MIME_TYPE
import base.BaseRenderer
from .. import utils

_logger = logging.getLogger(__name__)

class VegaRenderer (base.BaseRenderer):
    MIME_TYPES = (
        "application/vega",
        "application/vega-lite",)

    def render (self, content, content_type):
        # if the input content is a string, we attempt to parse it
        if (utils.is_string(content)):
            try:
                content = json.loads(content)
            except Exception as exception:
                raise Exception("Invalid JSON document: %s" % exception)

        # at that point the content should be an object,
        # which we dump into a valid JSON document
        try:
            vg_document = json.dumps(content,
                indent = 4, separators = (',', ': '))

        except Exception as exception:
            raise Exception("Invalid JSON document: %s" % exception)

        vg_container_id = str(uuid.uuid1()).replace('-', '_')
        vg_mode = {
            "application/vega": "vega",
            "application/vega-lite": "vega-lite"}[content_type]

        yield (core.MIME_TYPE.HTML,
            _HTML_TEMPLATE % {
                "vg_container_id": vg_container_id})

        yield (core.MIME_TYPE.JAVASCRIPT,
            _JAVASCRIPT_TEMPLATE % {
                "vg_mode": vg_mode,
                "vg_document": _indent(vg_document, 12),
                "vg_container_id": vg_container_id},
            {"modules": _JAVASCRIPT_MODULES})

def _indent (text, n_spaces):
    text_ = ''
    for line in text.splitlines(keepends = True):
        text_ += ' ' * n_spaces + line
    return text_

_JAVASCRIPT_MODULES = {
    # D3.js and various extensions
    "d3": "https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.16/d3.min.js",
    "d3-geo-projection": ("https://cdnjs.cloudflare.com/ajax/libs/d3-geo-projection/0.2.16/d3.geo.projection.min.js", ["d3"]),
    "d3-cloud": ("https://vega.github.io/vega-editor/vendor/d3.layout.cloud.js", ["d3"]),
    "topojson": "https://cdnjs.cloudflare.com/ajax/libs/topojson/1.6.20/topojson.min.js",

    # Vega, Vega-lite and Vega-embed
    "vg": ("https://cdnjs.cloudflare.com/ajax/libs/vega/2.5.1/vega.min.js", ["d3"]),
    "vl": ("https://vega.github.io/vega-lite/vega-lite.min.js", ["vg"]),
    "ve": ("https://vega.github.io/vega-editor/vendor/vega-embed.min.js", ["vg", "vl"])}

_JAVASCRIPT_TEMPLATE = """\
    var vg_specification = {
        mode: "%(vg_mode)s",
        spec: %(vg_document)s};

    vg.embed("#%(vg_container_id)s", vg_specification,
        function (error, chart) {
            if (error !== undefined) {
                console.log(error); }

            chart({el:"#%(vg_container_id)s"}).update();
        });
    """

_HTML_TEMPLATE = """\
    <div id="%(vg_container_id)s"></div>
    """
