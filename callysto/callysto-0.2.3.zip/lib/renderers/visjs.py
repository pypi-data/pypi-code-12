"""
Network renderer based on Vis.js; see
"""

__all__ = (
    "VisJsRenderer",)

import pydotplus

import core.MIME_TYPE
import base.BaseRenderer
from .. import utils

_logger = logging.getLogger(__name__)

class VisJsRenderer (base.BaseRenderer):
    MIME_TYPES = (
        "text/vnd.graphviz",)

    def render (self, content, content_type):
        # parse the DOT-formatted content
        try:
            g = pydotplus.graphviz.graph_from_dot_data(content)

        except Exception as e:
            raise Exception(
                "Unable to parse DOT document: %s; "
                "content was: %s" % (e, content))
