from lxml import etree
import logging

from .utils import process_transform, populate_transform
from .default import DefaultTagProcessor


logger = logging.getLogger(__name__)


NAMESPACEMAP = {
    None: "http://www.w3.org/2000/svg",
    "xlink" : 'http://www.w3.org/1999/xlink'
}

processors = {}


def tag_processor(tagname):
    def register_tag_processor(cls):
        processors[tagname] = cls()
        return cls
    return register_tag_processor


@tag_processor('Graphic')
class GraphicTagProcessor(DefaultTagProcessor):

    def on_start(self, target):
        attrs = target.attrs
        target.element = etree.Element(
            "svg",
            nsmap=NAMESPACEMAP,
            version="1.1",
            width=attrs.get("viewWidth"),
            height=attrs.get("viewHeight"),
            viewBox="0 0 %s %s" % (attrs.get("viewWidth"), attrs.get("viewHeight")),
            # viewport="0 0 %s %s" % (attrs.get("viewWidth"), attrs.get("viewHeight")),
            preserveAspectRatio="none",
            **{"enable-background": "new 0 0 %s %s" % (attrs.get("viewWidth"), attrs.get("viewHeight"))}
        )


@tag_processor('Library')
class LibraryTagProcessor(DefaultTagProcessor):

    def on_start(self, target):
        root = target.root
        target.element = etree.SubElement(root, "defs")


@tag_processor('Group')
class GroupTagProcessor(DefaultTagProcessor):
    def on_start(self, target):
        params = {}
        params.update(process_transform(**target.attrs))
        if 'alpha' in target.attrs:
            params['opacity'] = target.attrs['alpha']
        target.element = etree.SubElement(
            target.element,
            "g",
            **params
        )

    def on_end(self, target):
        if 'transform' in target.element.attrib:
            populate_transform(target.element)
        element = target.element
        parent = element.getparent()
        target.element = parent
