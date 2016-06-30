from lxml import etree
from PIL import Image
import uuid
import base64
from io import BytesIO

from .utils import process_transform
from .default import DefaultTagProcessor
from .common import NAMESPACEMAP


processors = {}


def tag_processor(tagname):
    def register_tag_processor(cls):
        processors[tagname] = cls()
        return cls
    return register_tag_processor


@tag_processor('BitmapImage')
class BitmapImageTagProcessor(DefaultTagProcessor):
    def on_start(self, target):
        params = {}
        params.update(process_transform(**target.attrs))
        if 'source' in target.attrs:
            src = target.attrs['source']
            if src.startswith('@Embed'):
                src = src[src.find("(") + 2:src.find(")") - 1]
                params['width'], params['height'] = map(lambda s: "%s" % s, Image.open(src).size)
                # *_, ext = src.split('.')
                # buffer = BytesIO()
                # Image.open(src).save(buffer, ext)
                # src = b"data:image/" + bytes(ext.lower(), encoding='utf8') + b";base64," + base64.b64encode(buffer.getvalue())
            params['{%s}href' % NAMESPACEMAP['xlink']] = src
        if 'width' in target.attrs:
            params['width'] = target.attrs['width']
        if 'height' in target.attrs:
            params['height'] = target.attrs['height']
        target.element = etree.SubElement(
            target.element,
            "image",
            **params
        )
