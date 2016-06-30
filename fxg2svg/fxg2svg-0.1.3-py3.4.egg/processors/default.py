from lxml import etree
import logging


logger = logging.getLogger(__name__)


class DefaultTagProcessor(object):

    def on_start(self, target):
        target.element = etree.SubElement(
            target.element,
            "foreignObject"
        )

    def on_end(self, target):
        parent = target.element.getparent()
        if parent is not None:
            target.element = parent
            self.process_children(target)


    def on_data(self, target):
        target.element.text = target.text


    def process_children(self, target):
        element = target.element
        clippathid = None
        for e in element:
            if clippathid:
                g = etree.SubElement(
                    element,
                    "g",
                    **{'clip-path': 'url(#%s)' % clippathid}
                )
                g.append(e)
            if e.tag == "clipPath":
                clippathid = e.attrib['id']

