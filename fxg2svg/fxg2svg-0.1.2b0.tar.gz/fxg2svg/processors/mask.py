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


def remove_group_elements(element, tag):
    for e in element:
        if tag == e.tag:
            for ch in e:
                remove_group_elements(ch, tag)
                element.append(ch)
            element.remove(e)


@tag_processor('mask')
class MaskTagProcessor(DefaultTagProcessor):
    def on_start(self, target):
        params = {}
        params['id'] = str(uuid.uuid4())
        target.element = etree.SubElement(
            target.element,
            "clipPath",
            # maskUnits="userSpaceOnUse",
            **params
        )

    def on_end(self, target):
        remove_group_elements(target.element, "g")
        super(MaskTagProcessor, self).on_end(target)
