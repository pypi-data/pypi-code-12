import io

import xml.etree.ElementTree as ET

def inc(fp):
    '''
    Create an table of contents of the article titles.

    :param fp: File-like object of XML
    :returns: Stream of of article title, file offset pairs
        (File offset is for the beginning of the line.)
    :rtype: iterable
    '''
    padleft = len(b'    <title>')
    padright = len(b'</title>\n')

    out = {}
    i = fp.tell()
    for line in fp:
        if line.startswith(b'    <title>'):
            yield line[padleft:-padright], i
        elif line == b'  </page>\n':
            i = fp.tell()

def dbname(fp):
    xml = ET.iterparse(fp)
    for _, element in xml:
        if element.tag == '{http://www.mediawiki.org/xml/export-0.10/}dbname':
            return element.text

def text(fp):
    path = './/{http://www.mediawiki.org/xml/export-0.10/}text'
    xml = ET.parse(fp)
    return xml.find(path).text + '\n'
