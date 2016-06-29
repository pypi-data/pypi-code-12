from lxml import etree
import re
import uuid
import math
import logging

from .default import DefaultTagProcessor


logger = logging.getLogger(__name__)
processors = {}


def tag_processor(tagname):
    def register_tag_processor(cls):
        processors[tagname] = cls()
        return cls
    return register_tag_processor


@tag_processor('SolidColor')
class SolidColorTagProcessor(DefaultTagProcessor):
    def on_start(self, target):
        color = target.attrs.get('color')
        if color:
            target.element.set(
                'fill', target.attrs.get('color')
            )
            if 'fill-opacity' in target.element.attrib:
                del target.element.attrib['fill-opacity']

    def on_end(self, target):
        pass


def rotate_point(x, y, a):
    alpha = a / 180 * math.pi 
    return (
        x * math.cos(alpha) - y * math.sin(alpha),
        x * math.sin(alpha) + y * math.cos(alpha),
    )


def get_coordinates(element):
    if element.tag == "rect":
        x = float(element.attrib.get('x', '0'))
        y = float(element.attrib.get('y', '0'))
        return x, y
    if element.tag == "path":
        x, y, *_ = re.findall(r'\d+\.\d+', element.attrib['d'])
        return float(x), float(y)
    return 0, 0


@tag_processor('RadialGradient')
class RadialGradientTagProcessor(DefaultTagProcessor):
    def on_start(self, target):
        x = float(target.attrs['x'])
        y = float(target.attrs['y'])
        scaleX = float(target.attrs['scaleX'])
        scaleY = float(target.attrs['scaleY'])
        offsetX, offsetY = get_coordinates(target.element)
        cx = offsetX + x
        cy = offsetY + y
        rx = scaleX / 2
        ry = scaleY / 2
        target.element = etree.SubElement(
            target.element,
            "radialGradient",
            cx=str(cx),
            cy=str(cy),
            rx=str(rx),
            ry=str(ry),
            id=str(uuid.uuid4())
        )

    def on_end(self, target):
        element = target.element
        target.element = element.getparent()
        target.defs.append(element)
        target.element.set('fill', 'url(#%s)' % element.attrib['id'])


@tag_processor('LinearGradient')
class LinearGradientTagProcessor(DefaultTagProcessor):
    def on_start(self, target):
        x = float(target.attrs['x'])
        y = float(target.attrs['y'])
        scaleX = float(target.attrs['scaleX'])
        rotation = float(target.attrs.get('rotation', '0'))
        offsetX, offsetY = get_coordinates(target.element)
        x1 = offsetX + x
        x2 = offsetX + x + scaleX
        y1 = offsetY + y
        y2 = offsetY + y
        x1, y1 = rotate_point(x1, y1, rotation)
        x2, y2 = rotate_point(x2, y2, rotation)
        target.element = etree.SubElement(
            target.element,
            "linearGradient",
            x1=str(x1),
            y1=str(y1),
            x2=str(x2),
            y2=str(y2),
            id=str(uuid.uuid4())
        )

    def on_end(self, target):
        element = target.element
        target.element = element.getparent()
        target.defs.append(element)
        target.element.set('fill', 'url(#%s)' % element.attrib['id'])


@tag_processor('GradientEntry')
class GradientEntryTagProcessor(DefaultTagProcessor):
    def on_start(self, target):
        target.element = etree.SubElement(
            target.element,
            "stop",
            offset=target.attrs.get('ratio', '1'),
            style="stop-color:%s" % target.attrs.get('color', '#000000'),
        )
