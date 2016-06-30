from lxml import etree

from .default import DefaultTagProcessor


processors = {}


def tag_processor(tagname):
    def register_tag_processor(cls):
        processors[tagname] = cls()
        return cls
    return register_tag_processor


@tag_processor('SolidColorStroke')
class SolidColorStrokeTagProcessor(DefaultTagProcessor):
    def on_start(self, target):
        color = target.attrs.get('color', '#000000')
        target.element.set(
            'stroke', color
        )
        strokewidth = target.attrs.get('weight')
        if strokewidth:
            target.element.set(
                'stroke-width', strokewidth 
            )
        strokemiterlimit = target.attrs.get('miterLimit')
        if strokemiterlimit:
            target.element.set(
                'stroke-miterlimit', strokemiterlimit 
            )

    def on_end(self, target):
        pass
