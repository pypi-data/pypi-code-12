import re
from xml.etree import cElementTree


namespace_re = re.compile('{[^}]*}')


class SitemapParsingException(Exception):
    pass


def dictify(element):
    return {unicode(child.tag): dictify(child) for child in element} \
        or unicode(element.text).strip()

def strip_namespaces(root):
    for element in root.iter():
        # Removing namespaces, sorry
        if isinstance(element.tag, basestring):
            # Sometimes <built-in function Comment>
            element.tag = namespace_re.sub('', element.tag)


class SitemapIndex(object):

    def __init__(self, xml):
        self.root = cElementTree.fromstring(xml)
        if self.root is None:
            raise SitemapParsingException('Unknown parsing error')
        strip_namespaces(self.root)
        self.sitemapindex = list(self._parse_sitemapindex(self.root))

    @staticmethod
    def _parse_sitemapindex(root):
        if not root.tag == 'sitemapindex':
            raise SitemapParsingException(
                'No sitemapindex found (tag: {tag})'.format(tag=root.tag))
        for sitemap in root:
            if not sitemap.tag == 'sitemap':
                continue
            if not 'loc' in [elem.tag for elem in sitemap.getchildren()]:
                continue
            yield dictify(sitemap)

    def __iter__(self):
        return iter(self.sitemapindex)


class Sitemap(object):

    def __init__(self, xml):
        self.root = cElementTree.fromstring(xml)
        if self.root is None:
            raise SitemapParsingException('Unknown parsing error')
        strip_namespaces(self.root)
        self.urlset = list(self._parse_urlset(self.root))

    @staticmethod
    def _parse_urlset(root):
        if not root.tag == 'urlset':
            raise SitemapParsingException(
                'No urlset found (tag: {tag})'.format(tag=root.tag))
        for url in root:
            if not url.tag == 'url':
                continue
            if not 'loc' in [elem.tag for elem in url.getchildren()]:
                continue
            yield dictify(url)

    def __iter__(self):
        return iter(self.urlset)
