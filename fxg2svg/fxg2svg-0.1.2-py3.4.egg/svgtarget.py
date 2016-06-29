from lxml import etree
from .processors import all_processors as procs
import logging


logger = logging.getLogger(__name__)


def remove_namespace(namespaced):
    *_, unnamespaced = namespaced.split("}")
    return unnamespaced


def process_attrs(attrs):
    new_attrs = {}
    for attrname, attrvalue in attrs.items():
        new_attrs[remove_namespace(attrname)] = attrvalue
    return new_attrs


class SVGTarget(object):

    def __init__(self):
        self.element = None
        self.tagname = None
        self.attrs = {}
        self.depth = 0
        self.text = None
        self.svg = []
        self.fxg = []

    def start(self, tagname, attrs):
        self.tagname = remove_namespace(tagname)
        self.attrs = process_attrs(attrs)
        procs[self.tagname].on_start(self)
        self.svg.append((self.element.tag, self.element.attrib))
        self.fxg.append((self.tagname, self.attrs))

    def end(self, tagname):
        self.tagname = remove_namespace(tagname)
        try:
            self.svg.pop()
            self.fxg.pop()
        except IndexError:
            pass
        procs[self.tagname].on_end(self)

        self.text = None
        self.attrs = {}
        self.tagname = None

    def data(self, data):
        self.text = data
        procs[self.tagname].on_data(self)

    def close(self):
        return self.root

    @property
    def root(self):
        return self.element.getroottree().getroot()

    @property
    def defs(self):
        return self.element.getroottree().find('defs')

    def get_attribute(self, attrname):
        for event in self.fxg:
            tag, attrs = event
            if attrname in attrs:
                return attrs[attrname]
