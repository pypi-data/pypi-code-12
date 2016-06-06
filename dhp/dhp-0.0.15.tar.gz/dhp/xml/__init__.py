'''routines generally helpful for dealing with icky xml'''
# std py3k stanza
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import defaultdict
from decimal import Decimal
import warnings
from xml.dom.minidom import getDOMImplementation, parseString
from xml.etree import cElementTree as ElementTree
from xml.etree.cElementTree import ParseError

from dhp.VI import iteritems, InstanceType, py_ver


# pylint: disable=W0141
def _etree_to_dict(tree):
    '''transform element tree to a dictionary'''
    d_parent = {tree.tag: {} if tree.attrib else None}
    children = list(tree)

    if children:
        # make __missing__ returns an empty list
        dd_l = defaultdict(list)
        for d_child in map(_etree_to_dict, children):
            for k, val in iteritems(d_child):
                dd_l[k].append(val)

        temp = {}
        for k, val in iteritems(dd_l):
            if len(val) == 1:
                temp[k] = val[0]
            else:
                temp[k] = val
        d_parent = {tree.tag: temp}

    if tree.attrib:
        d_parent[tree.tag].update(('@' + k, val)
                                  for k, val in iteritems(tree.attrib))

    if tree.text:
        text = tree.text.strip()

        if children or tree.attrib:
            if text:        # pragma: no cover
                d_parent[tree.tag]['#text'] = text
        else:
            d_parent[tree.tag] = text

    return d_parent


def xml_to_dict(xml_buf):
    '''convert xml string to a dictionary, not always pretty, but reliable'''

    eltree = ElementTree.XML(xml_buf)
    return _etree_to_dict(eltree)


class NoRootExeception(Exception):
    '''raised when dictionary to build xml document from does not have a
    single 'root' node elment.  i.e.  ``{'root':{ ... }}`` '''
    pass


def _dict_to_doc(dictionary, attrs=None):
    '''give a dictionary, (and possibly attributes) return an xml
    document representation of same.'''
    if len(dictionary) != 1:
        raise NoRootExeception
    if not isinstance(list(dictionary.values())[0], dict):
        raise NoRootExeception

    impl = getDOMImplementation()
    doc = impl.createDocument(None, list(dictionary.keys())[0], None)

    def dict_to_nodelist(dictionary, parent):
        '''express the dictonary as a nodelist'''
        for key, child in iteritems(dictionary):
            new = doc.createElement(key)
            parent.appendChild(new)
            if isinstance(child, dict):
                dict_to_nodelist(child, new)
            else:
                new.appendChild(doc.createTextNode(child))

    if attrs:
        for key, val in iteritems(attrs):
            doc.documentElement.setAttribute(key, val)

    dict_to_nodelist(list(dictionary.values())[0], doc.documentElement)
    return doc


def dict_to_xml(dictionary, attrs=None):
    '''return a string representation of an xml document of the dictionary. (
    with optional attributes for the root node.)

    >>> the_dict = {'root': {'foo': '1'}}
    >>> dict_to_xml(the_dict)
    <?xml version="1.0" ?><root xml:lang="en-US"><foo>1</foo></root>

    Since the function returns a full xml document, the dictionary has to
    closely approximate the structure of the xml document.  So the top level of
    the dictionary must be a string key with a dictionary for a value.

    Also, ALL leaf node  element values must be strings.

    Args:
        dictionary (dict): an approximation of the xml document desired as a
                           Python dictionary.
        args (dict): a dicitionary containing attributes to assign to the root
                     level node.

    Raises:
        NoRootExeception : When there top level dictionary has more than 1
                           key/value or if the value of the top level key is
                           not a dictionary.
    Returns:
        str : a string representing an xml document based on the inputs.

    '''
    return _dict_to_doc(dictionary, attrs).toxml()


def ppxml(xmls, indent='  '):
    '''pretty print xml, stripping an existing formatting

    >>> buf = '<root><foo>1</foo></root>'
    >>> ppxml(buf)
    <?xml version="1.0" ?>
    <root>
      <foo>1</foo>
    </root>

    Args:
        xmls (str): an xml string, either a fragment or document
        indent (str): a string containing the white space to use for
                      indentation.

    Returns:
        str : A transform of that string with new lines and standardized
              indentation. Default is 2 spaces ``indent='  '``
    '''
    xml_doc = parseString(xmls)
    better_xml = xml_doc.toprettyxml(indent=indent)
    outbuf = ''
    for line in better_xml.split('\n'):
        if len(line.strip()):
            outbuf += line
            outbuf += '\n'
    return outbuf


def _is_udo(obj):
    '''return True if obj is a user Defined Object'''
    if isinstance(obj, (Decimal, dict, int, float, list, set, str)):
        return False
    if py_ver() < 3:
        if isinstance(obj, InstanceType):
            return True
    if str(type(obj)).startswith('<class'):
        return True
    return False


def _make_xml_element(name, value):
    '''return an xml element'''
    if value is None:
        return ''
    return '<%s>%s</%s>' % (name, obj_to_xml(value), name)


class MissingRequiredException(Exception):
    '''A required data element is not present'''
    pass


def _verify_elements(obj):
    '''see if required or known elements are listed, if so review the
    objects.__dict__ for expressed elements to see that they have all required
    elements and warn if some expressed are not in the known list.'''
    # gather specifications, if available
    obj_name = obj.__class__.__name__
    required = getattr(obj, '_%s__required_elements' % obj_name, {})
    known = getattr(obj, '_%s__known_elements' % obj_name, {})
    missing_required = []
    unknown = []
    # look for missing Required
    for key in required.keys():
        if obj.__dict__.get(key, None) is None:
            missing_required.append(key)
    # look for unknown elements if specified
    if known:   # only process if 1 or more know are specified
        required_or_known = {}
        required_or_known.update(required)
        required_or_known.update(known)    # ignore required
        for key in obj.__dict__:
            if not key.startswith('_'):
                if key not in required_or_known:
                    unknown.append(key)
    # look for exceptions and report
    if missing_required or unknown:
        if missing_required:
            raise MissingRequiredException('The following required are '
                                           'missing: %s' % missing_required)
        if unknown:
            warnings.warn('unknown: %s' % sorted(unknown), SyntaxWarning)
    return


def obj_to_xml(obj):
    '''serialize an object's non-private/non-hidden data attributes'''
    if _is_udo(obj):
        name = getattr(obj, '_name', None) or obj.__class__.__name__
        _verify_elements(obj)
        return _make_xml_element(name, obj.__dict__)
    elif isinstance(obj, dict):
        buf = ''
        for attr in sorted(obj.keys()):
            if not attr.startswith('_'):
                buf += _make_xml_element(attr, obj[attr])
        return buf
    elif isinstance(obj, list):
        buf = ''
        for item in obj:
            if _is_udo(item):
                buf += obj_to_xml(item)
            else:
                buf += _make_xml_element("item", item)
        return buf

    else:
        return obj
