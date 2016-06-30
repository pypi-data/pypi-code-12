from lxml import etree

from .utils import process_transform
from .default import DefaultTagProcessor


processors = {}


def tag_processor(tagname):
    def register_tag_processor(cls):
        processors[tagname] = cls()
        return cls
    return register_tag_processor


@tag_processor('Path')
class PathTagProcessor(DefaultTagProcessor):
    def on_start(self, target):
        params = {}
        params['d'] = target.attrs['data']
        params.update(process_transform(**target.attrs))
        target.element = etree.SubElement(
            target.element,
            "path",
            **params
        )


@tag_processor('Rect')
class RectTagProcessor(DefaultTagProcessor):
    def on_start(self, target):
        params = {}
        if 'radiusX' in target.attrs:
            params['rx'] = target.attrs['radiusX']
        if 'radiusY' in target.attrs:
            params['ry'] = target.attrs['radiusY']
        if 'alpha' in target.attrs:
            params['opacity'] = target.attrs['alpha']
        params['fill-opacity'] = '0'
        target.element = etree.SubElement(
            target.element,
            "rect",
            x="%s" % target.attrs.get("x", "0"),
            y="%s" % target.attrs.get("y", "0"),
            width="%s" % target.attrs.get("width"),
            height="%s" % target.attrs.get("height"),
            **params
        )


@tag_processor('Ellipse')
class EllipseTagProcessor(DefaultTagProcessor):
    def on_start(self, target):
        params = {}
        if 'alpha' in target.attrs:
            params['opacity'] = target.attrs['alpha']
        target.element = etree.SubElement(
            target.element,
            "ellipse",
            cx="%s" % (float(target.attrs.get("x")) + float(target.attrs.get("width")) / 2),
            cy="%s" % (float(target.attrs.get("y")) + float(target.attrs.get("height")) / 2),
            rx="%s" % (float(target.attrs.get("width")) / 2),
            ry="%s" % (float(target.attrs.get("height")) / 2),
            **params
        )



@tag_processor('Line')
class LineTagProcessor(DefaultTagProcessor):
    def on_start(self, target):
        params = {}
        target.element = etree.SubElement(
            target.element,
            "line",
            x1="%s" % target.attrs.get("xFrom"),
            y1="%s" % target.attrs.get("yFrom"),
            x2="%s" % target.attrs.get("xTo"),
            y2="%s" % target.attrs.get("yTo"),
            **params
        )
