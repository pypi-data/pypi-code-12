
"""
About
=====
This is simple python module to parse html to A href values.

It can also do it recurcively accordingly to maxdepth parameter or as
deep as it can if maxdepth == -1

An html can be a file or a http server output.
"""

import xml.dom.minidom
import urllib
import re
import logging


def html_walk(html_text, maxdepth=10):
    """
    TODO
    """
    # TODO: todo
    pass


def list_rm_douplicates(lst=[]):
    """
    Routine for removal duplicated items from text list
    """
    lst2 = []

    for i in lst:
        if not i in lst2:
            lst2.append(i)

    return lst2


def html_link_get_links(url, tag_attr=[
        ('a', 'href'),
        # ('img', 'src'),
        # ('script', 'src')
        ]):
    """
    Tryes to open url, get it's content-type and if content-type is
    text/html - feed it to L{html_text_get_links}

    TODO

    @type url: text

    @param tag_attr: see L{dom_get_links}

    @return: link list on success or None on error

    @rtype: list or None
    """

    ret = None

    url_object = urllib.request.urlopen(url)
    ct = url_object.info().getheader('content-type').lower().strip()

    re_res = re.match(r'text/html(; *codepage=(.*))?', ct)

    if re_res is not None and re_res.group(
            1) is not None and re_res.group(2) is not None:

        text = url_object.read().decode(re_res.group(2))
        ret = html_text_get_links(text, tag_attr)

        if ret is None:
            logging.error(
                "Can't parse document " +
                url +
                " as XML (codepage:" +
                repr(
                    re_res.group(2)) +
                ")")

    # cleaningup for sure
    url_object.close()
    del url_object
    del re_res

    return ret


def html_text_get_links(html_text, base_url, tag_attr=[
        ('a', 'href'),
        # ('img', 'src'),
        # ('script', 'src')
        ]):
    """
    Parses text to xml.dom and feeds it to L{dom_get_links}

    Uses L{dom_get_links}, L{list_rm_douplicates} and
    L{list_rm_douplicates}.

    Returned list will be sorted alphabeticly.

    @type html_text: text

    @param base_url: used for expanding relative links

    @type base_url: text

    @param tag_attr: see L{dom_get_links}

    @return: list on success or None on error

    @rtype: list or None

    """
    docum = None
    try:
        docum = xml.dom.minidom.parseString(html_text)
    except:
        # print "-e- Can't parse text as XML"
        return None

    root = docum.documentElement
    lst = sorted(dom_get_links(root))
    lst = list_rm_douplicates(lst)
    return lst

# def expand_links(lst=[], cwd=''):
#     """
#     Not completed
#     """
#     lst2 = []

#     for i in lst:
#         if not i in lst2:
#             lst2.append(i)

#     return lst2


def dom_get_links(root, tag_attr=[
        ('a', 'href'),
        # ('img', 'src'),
        # ('script', 'src')
        ]):
    """
    Get all <a href=""> links from domain xml.dom objects recurcively

    @param root: xml.dom object

    @param tag_attr: list of tuples, each of which has two values:

       0. tagname for which to look

       1. this tag attribute name which to add to returnable list.

    @return: list with all links in xml.dom object

    @rtype: list
    """
    lst = []

    for i in root.childNodes:
        if i.nodeType == xml.dom.Node.ELEMENT_NODE:

            if len(i.childNodes) > 0:
                lst += dom_get_links(i)

            for tag, attr in tag_attr:

                if i.tagName == tag:
                    if i.hasAttribute(attr):
                        t = i.getAttribute(attr)
                        lst.append(t)
                        del t

    return lst
