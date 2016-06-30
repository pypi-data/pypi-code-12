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
        ct_params = {}

        if 'blurX' in attrs and 'blurY' in attrs:
            if round(float(attrs['blurX'])) == round(float(attrs['blurY'])):
                blur_params['stdDeviation'] = attrs['blurX']
            else:
                blur_params['stdDeviation'] = "%s %s" % (
                    attrs['blurX'], attrs['blurY'])

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

        if 'alpha' in attrs:
            ct = etree.SubElement(
                filter,
                "feComponentTransfer",
                **{'in': current_state, 'result': 'ctResult'}
            )
            etree.SubElement(
                ct,
                "feFuncA",
                **{"type": "linear", "slope": attrs['alpha']}
            )
            current_state = 'ctResult'

        merge = etree.SubElement(
            filter,
            "feMerge"
        )
        etree.SubElement(
            merge,
            "feMergeNode",
            **{"in": current_state}
        )
        etree.SubElement(
            merge,
            "feMergeNode",
            **{"in": "SourceGraphic"}
        )
                
        target.element.set('filter', 'url(#%s)' % filter_params['id'])
        return target.element

    def on_end(self, target):
        pass
