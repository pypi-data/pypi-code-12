import os
from xml.etree.ElementTree import Element, SubElement, tostring


class Sitemap:

    def __init__(self, filename, quiet=False):
        self.validate(filename)
        self.filepath = os.path.join(os.getcwd(), filename)
        self.quiet = quiet

    def validate(self, filename):
        if not filename:
            raise Exception('need to specify filename to write to')

    def write_to_file(self, xml):
        with open(self.filepath, 'w') as sitemap:
            sitemap.write(tostring(xml).decode('utf-8'))

    def create_xml_node(self, root, link):
        url = SubElement(root, 'url')
        loc = SubElement(url, 'loc')
        loc.text = link

    def create_xml(self, links):
        root = Element('urlset')
        root.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
        root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        root.set('xsi:schemaLocation', 'http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd')
        for i, link in enumerate(links):
            self.create_xml_node(root, link)
        return root

    def run(self, links):
        xml = self.create_xml(links)
        self.write_to_file(xml)
        if self.quiet is not True:
            print('wrote sitemap to {}'.format(self.filepath))
