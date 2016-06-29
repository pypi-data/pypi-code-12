from lxml import etree
from PIL import Image, ImageFont, ImageDraw
import logging

from .utils import process_transform, get_attribute
from .default import DefaultTagProcessor


def get_font_size(letters, fontsize=None, fontname=''):
    if fontsize:
        font = ImageFont.truetype('/home/hus/.local/share/fonts/ufonts.com_century-gothic-bold.ttf', fontsize)
    else:
        font = ImageFont.truetype('/home/hus/.local/share/fonts/ufonts.com_century-gothic-bold.ttf')
    return font.getsize(letters)[1]


def process_font(**attrs):
    params = {}
    if 'fontFamily' in attrs:
        params['font-family'] = attrs['fontFamily']
    if 'fontSize' in attrs:
        params['font-size'] = attrs['fontSize']
    if 'fontWeight' in attrs:
        params['font-weight'] = attrs['fontWeight']
    if 'color' in attrs:
        params['fill'] = attrs['color']
    if 'textAlign' in attrs:
        params['text-anchor'] = {
            'left': 'start',
            'center': 'middle',
            'right': 'end',
        }[attrs['textAlign']]
    if 'lineHeight' in attrs:
        params['line-height'] = attrs['lineHeight']
    if 'fontStyle' in attrs:
        params['font-style'] = attrs['fontStyle']
    return params


processors = {}
logger = logging.getLogger(__name__)


def tag_processor(tagname):
    def register_tag_processor(cls):
        processors[tagname] = cls()
        return cls
    return register_tag_processor


@tag_processor('RichText')
class RichTextTagProcessor(DefaultTagProcessor):

    def on_start(self, target):
        params = {}
        params.update(process_transform(**target.attrs))
        params.update(process_font(**target.attrs))
        target.element = etree.SubElement(
            target.element,
            "text",
            **params
        )


def get_recursive_data(element):
    text = element.text or ''
    for e in element:
        text += get_recursive_data(e)
    return text


@tag_processor('p')
class PTagProcessor(DefaultTagProcessor):

    def on_start(self, target):
        params = {}
        params.update(process_transform(**target.attrs))
        params.update(process_font(**target.attrs))
        params['x'] = b'0'
        params['dy'] = b'0.75em'
        target.element = etree.SubElement(
            target.element,
            "tspan",
            **params
        )

    def on_end(self, target):
        super(PTagProcessor, self).on_end(target)
        text = get_recursive_data(target.element)
        lineheight = get_attribute(target.element, 'line-height')
        fontsizeattr = get_attribute(target.element, 'font-size')
        if fontsizeattr:
            fontsizeattr = int(float(fontsizeattr))
        dy = get_font_size(text, fontsize=fontsizeattr)
        if lineheight:
            lineheight = float(lineheight)
            dy = max([lineheight, dy])
        target.element.set('dy', str(dy))


@tag_processor('span')
class SpanTagProcessor(PTagProcessor):
    def on_start(self, target):
        params = {}
        params.update(process_transform(**target.attrs))
        params.update(process_font(**target.attrs))
        target.element = etree.SubElement(
            target.element,
            "tspan",
            **params
        )

    def on_data(self, target):
        super(SpanTagProcessor, self).on_data(target)
        typographic_case = target.get_attribute('typographicCase')
        logger.debug(typographic_case)
        logger.debug(target.tagname)
        logger.debug(target.element.text)
        if typographic_case:
            if typographic_case == "uppercase":
                target.element.text = target.text.upper()
            if typographic_case == "lowercase":
                target.element.text = target.text.lower()
