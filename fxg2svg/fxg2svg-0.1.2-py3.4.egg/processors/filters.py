from lxml import etree
import uuid

from .utils import process_transform
from .default import DefaultTagProcessor


processors = {}


def tag_processor(tagname):
    def register_tag_processor(cls):
        processors[tagname] = cls()
        return cls
    return register_tag_processor


@tag_processor('DropShadowFilter')
class PathTagProcessor(DefaultTagProcessor):
    def on_start(self, target):
        attrs = target.attrs
        params = {}
        defs = target.defs
        filter_params = {
            'id': str(uuid.uuid4()),
            'width': '250%',
            'height': '250%',
            'x': '-50%',
            'y': '-50%'
        }
        filter = etree.SubElement(
            defs,
            "filter",
            **filter_params
        )
        offset_params = {}
        blur_params = {}

        if 'blurX' in attrs and 'blurY' in attrs:
            blur_params['stdDeviation'] = "%s %s" % (attrs['blurX'], attrs['blurY'])
        if 'distance' in attrs:
            offset_params['dx'] = attrs['distance']
            offset_params['dy'] = attrs['distance']

        current_state = 'SourceAlpha'

        if len(offset_params.keys()) > 0:
            offset_params['in'] = current_state
            offset_params['result'] = 'offsetResult'
            current_state = offset_params['result']
            etree.SubElement(
                filter,
                "feOffset",
                **offset_params
            )

        if len(blur_params.keys()) > 0:
            blur_params['in'] = current_state
            blur_params['result'] = 'blurResult'
            current_state = blur_params['result']
            etree.SubElement(
                filter,
                "feGaussianBlur",
                **blur_params
            )

        blend_params = {
            'in': 'SourceGraphic',
            'mode': 'normal'
        }
        if current_state != 'SourceGraphic':
            blend_params['in2'] = current_state
        etree.SubElement(
            filter,
            "feBlend",
            **blend_params
        )
                
        target.element.set('filter', 'url(#%s)' % filter_params['id'])
        return target.element

    def on_end(self, target):
        pass
