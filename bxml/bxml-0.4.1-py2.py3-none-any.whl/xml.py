
import os, re, time, sys, subprocess, html, json, tempfile, traceback
from copy import deepcopy
from lxml import etree
from bl.dict import Dict
from bl.id import random_id
from bl.string import String
from bf.file import File

from .schema import Schema

class XML(File):

    def __init__(self, fn=None, root=None, tree=None, parser=None, encoding='UTF-8', schemas=None, **args):
        File.__init__(self, fn=fn, root=root, info=None, parser=parser, schemas=schemas, **args)

        # set up the root element
        if root is None and tree is not None:
            self.root = self.tree.getroot()
        elif type(root) in [str, bytes]:
            self.root = XML.fromstring(root, parser=parser)
        elif root is not None:
            self.root = root
        elif type(fn) in [str, bytes]:                          # read from fn
            tree = etree.parse(fn, parser=parser)
            self.root = tree.getroot()
            self.info = self.get_info(tree=tree)
        elif self.ROOT_TAG is not None:
            self.root = etree.Element(self.ROOT_TAG)
        else:
            self.root = etree.Element(String(self.__class__.__name__).identifier(camelsplit=True).lower())

        # set up document info (based on tree.docinfo)
        if self.info is None:
            self.info = self.get_info(tree=tree)

    @classmethod
    def get_info(c, tree=None):
        if tree is not None:
            docinfo = tree.docinfo
            return Dict(
                    URL = docinfo.URL,
                    doctype = docinfo.doctype,
                    root_name = docinfo.root_name,
                    xml_version = docinfo.xml_version,
                    encoding = docinfo.encoding)
        else:
            return Dict()

    @classmethod
    def href_to_id(C, href):
        return String(href).identifier()

    @classmethod
    def xpath(C, node, path, namespaces=None, extensions=None, smart_strings=True, **args):
        """shortcut to Element.xpath()"""
        return node.xpath(path, namespaces=namespaces, extensions=extensions, smart_strings=smart_strings, **args)

    @classmethod
    def find(C, node, path, namespaces=None, extensions=None, smart_strings=True, **args):
        """use Element.xpath() rather than Element.find() in order to normalize the interface"""
        xp = node.xpath(path, namespaces=namespaces, extensions=extensions, smart_strings=smart_strings, **args)
        if len(xp) > 0:
            return xp[0]


    def write(self, fn=None, root=None, encoding=None, doctype=None, 
            xml_declaration=True, pretty_print=True, with_comments=True):
        data = self.tobytes(root=root or self.root, 
                    xml_declaration=xml_declaration, pretty_print=pretty_print,
                    encoding=encoding or self.info.encoding or 'UTF-8',
                    doctype=doctype or self.info.doctype,
                    with_comments=with_comments)
        File.write(self, fn=fn or self.fn, data=data)

    def tobytes(self, root=None, encoding=None, doctype=None, 
            xml_declaration=True, pretty_print=True, with_comments=True):
        """return the content of the XML document as a byte string suitable for writing"""
        if root is None: root = self.root
        return etree.tostring(root, 
            encoding=encoding or self.info.encoding or 'UTF-8',
            doctype=doctype or self.info.doctype, 
            xml_declaration=xml_declaration, 
            pretty_print=pretty_print, 
            with_comments=with_comments)

    def __bytes__(self):
        return self.tobytes(pretty_print=True)

    def tostring(self, root=None, doctype=None, pretty_print=True):
        """return the content of the XML document as a unicode string"""
        if root is None: root = self.root
        return etree.tounicode(root, 
            doctype=doctype or self.info.doctype, 
            pretty_print=pretty_print)

    def __str__(self):
        return self.tostring(pretty_print=True)

    def __unicode__(self):
        return self.__str__()

    def copy(self, elem=None):
        d = self.__class__()
        for k in self.keys():
            d[k] = deepcopy(self[k])
        d.root = deepcopy(self.root)
        return d

    @classmethod
    def Element(cls, s, *args):
        """given a string s and string *args, return an Element."""
        sargs = []
        for arg in args:
            if type(arg) == etree._Element:
                sargs.append(etree.tounicode(arg))
            else:
                sargs.append(arg)
        if type(s)==etree._Element:
            t = etree.tounicode(s)
        else:
            t = s
        if len(args)==0:
            return XML.fromstring(t)
        else:
            return XML.fromstring(t % tuple(sargs))
    
    @classmethod
    def fromstring(Class, text, parser=None, base_url=None, encoding='UTF-8'):
        if type(text)==str:
            text = text.encode(encoding)
        return etree.fromstring(text, parser=parser, base_url=base_url)

    # == VALIDATION == 
    # uses the Schema object in this module

    def Validator(self, tag=None, schemas=None, rebuild=False): # ADD CACHEING
        tag = tag or self.root.tag
        schemas = schemas or self.schemas
        rngfn = Schema.filename(tag, schemas, ext='.rng')
        if not os.path.exists(rngfn) or rebuild==True:          # .rnc => .rng
            rncfn = Schema.filename(tag, schemas, ext='.rnc')
            if os.path.exists(rncfn):
                rngfn = Schema(rncfn).trang(ext='.rng')
        return etree.RelaxNG(etree.parse(rngfn))

    def assertValid(self, tag=None, schemas=None):
        validator = self.Validator(tag=tag, schemas=schemas)
        validator.assertValid(self.root)
    
    def validate(self, tag=None, schemas=None, jing=True, relax=False):
        errors = []
        if relax==True:
            try:
                self.assertValid(tag=tag, schemas=schemas)
            except:
                errors += [str(sys.exc_info()[1]).strip()]
        if jing==True:
            try:
                self.jing(tag=tag, schemas=schemas)
            except:
                errors += str(sys.exc_info()[1]).split('\n')
        return errors

    def isvalid(self, tag=None, schemas=None):
        try:
            self.assertValid(tag=tag, schemas=schemas)
            return True
        except:
            return False

    def jing(self, tag=None, schemas=None, ext='.rnc'):
        """use the (included) jing library to validate the XML."""
        from . import JARS
        jingfn = os.path.join(JARS, 'jing.jar')
        tag = tag or self.root.tag
        schemas = schemas or self.schemas
        schemafn = Schema.filename(tag, schemas, ext=ext)
        if schemafn is not None:
            try:
                fn = self.fn
                tempf = None
                if fn is None:
                    tempf = tempfile.NamedTemporaryFile()
                    tempf.write(etree.tounicode(self.root).encode('utf-8'))
                    fn = tempf.name
                self.log("fn = %s, tag = %s, schema = %s" % (self.fn, tag, schemafn))
                subprocess.check_output(['java', '-jar', jingfn, '-c', schemafn, fn])
                if tempf is not None:
                    tempf.close()
            except subprocess.CalledProcessError as e:
                tbtext = html.unescape(str(e.output, 'UTF-8'))
                raise RuntimeError(tbtext).with_traceback(sys.exc_info()[2]) from None

    # == NAMESPACE == 

    def namespace(self, elem=None):
        """return the URL, if any, for the doc root or elem, if given."""
        if elem is None: elem = self.root
        return XML.tag_namespace(elem.tag)

    @classmethod
    def tag_namespace(cls, tag):
        """return the namespace for a given tag, or '' if no namespace given"""
        md = re.match("^(?:\{([^\}]*)\})?", tag)
        return md.group(1) or md.group(0)

    @classmethod
    def tag_name(cls, tag):
        """return the name of the tag, with the namespace removed"""
        return re.sub("{"+cls.tag_namespace(tag)+"}", "", tag)

    # == TRANSFORMATIONS == 

    def xslt(self, xslfn, elem=None, cache=True, **params):
        from .xslt import XSLT
        xt = XSLT(fn=xslfn, elem=elem, cache=cache)
        return xt(elem, **params)

    def transform(self, transformer, elem=None, fn=None, DocClass=None, **params):
        if DocClass==None: DocClass = self.__class__
        if elem is None: elem = self.root
        if fn is None: fn = self.fn
        return DocClass(
                root=transformer.Element(elem, xml=self, fn=fn, **params),
                fn=fn)

    # == AUDITING == 

    def num_words(self):
        t = etree.tounicode(self.root, method="text").strip()
        words = re.split("\s+", t)
        return len(words)
        
    def tag_dict(self, tags={}, exclude_attribs=[]):
        """returns a dict of the tags and comments that occur in an XML document"""
        for elem in self.root.xpath("//*"):
            if elem.tag not in tags:
                tags[elem.tag] = {}
            for a in elem.attrib:
                if a not in exclude_attribs:
                    if a not in tags[elem.tag]:
                        tags[elem.tag][a] = []
                    if elem.get(a) not in tags[elem.tag][a]:
                        tags[elem.tag][a].append(elem.get(a))
        for comment in self.root.xpath("//comment()"):
            c = str(comment).strip("<>")
            if c not in tags:
                tags[c] = {}
        return tags

    # == CONVERSIONS == 

    def as_json(self, elem=None, indent=None, ignore_whitespace=True, namespaces=False):
        return json.dumps(
            self.as_dict(elem=elem, ignore_whitespace=ignore_whitespace, namespaces=namespaces), 
            indent=indent)

    def as_dict(self, elem=None, ignore_whitespace=True, namespaces=False):
        """Create a generalized dict output from this elem (default self.root).
        Rules:
            * Elements are objects with a single attribute, which is the tag name.
            * The value of the single attribute is a list. The elements of the list are:
                o a dict containing attributes
                + zero or more strings or objects. 
                    - text is represented as strings
                    - elements are represented as objects
        If ignore_whitespace==True, then whitespace-only element text and tail will be omitted.
        If namespaces==True, then include the namespaces in the element/attribute names.
        Comments and processing instructions are ignored.
        The "tail" of the root node is also ignored.
        """
        if elem is None: elem = self.root
        if namespaces == False:
            tag = re.sub("^\{[^\}]*\}", "", elem.tag)
        else:
            tag = elem.tag
        attrib = Dict(**elem.attrib)
        if namespaces == False:
            for key in attrib:
                newkey = re.sub("^\{[^\}]*\}", "", key)
                attrib[newkey] = attrib.pop(key)
        d = Dict(**{tag: [attrib]})
        if elem.text is not None and (elem.text.strip() != '' or ignore_whitespace != True): 
            d[tag].append(elem.text)
        for ch in [e for e in elem if type(e) == etree._Element]:   # *** IGNORE EVERYTHING EXCEPT ELEMENTS ***
            d[tag].append(self.as_dict(elem=ch))
            if elem.tail is not None and (elem.tail.strip() != '' or ignore_whitespace != True):
                d[tag].append(elem.tail)
        return d

    # == TREE MANIPULATIONS == 

    @classmethod
    def is_empty(c, elem):
        return elem.text in [None, ''] and len(elem.getchildren())==0

    @classmethod
    def remove_if_empty(c, elem, leave_tail=True):
        if c.is_empty(elem):
            c.remove(elem, leave_tail=leave_tail)

    @classmethod
    def replace_with_contents(c, elem):
        "removes an element and leaves its contents in its place. Namespaces supported."
        parent = elem.getparent()
        index = parent.index(elem)
        children = elem.getchildren()
        previous = elem.getprevious()
        # text
        if index==0:
            parent.text = (parent.text or '') + (elem.text or '')
        else:
            previous.tail = (previous.tail or '') + (elem.text or '')
        # children
        for child in children:
            parent.insert(index + children.index(child), child)
        # tail
        if len(children) > 0:
            last_child = children[-1]
            last_child.tail = (last_child.tail or '') + (elem.tail or '')
        else:
            if index==0:
                parent.text = (parent.text or '') + (elem.tail or '')
            else:
                previous.tail = (previous.tail or '') + (elem.tail or '')
        # elem
        parent.remove(elem)

    @classmethod
    def remove(c, elem, leave_tail=True):
        parent = elem.getparent()
        if leave_tail==True:
            if parent.index(elem)==0:
                parent.text = (parent.text or '') + (elem.tail or '')
            else:
                prev = elem.getprevious()
                prev.tail = (prev.tail or '') + (elem. tail or '')
        parent.remove(elem)

    @classmethod
    def remove_range(cls, elem, end_elem, delete_end=True):
        """delete everything from elem to end_elem, including elem.
        if delete_end==True, also including end_elem; otherwise, leave it."""
        while elem is not None and elem != end_elem \
        and end_elem not in elem.xpath("descendant::*"):
            parent = elem.getparent()
            nxt = elem.getnext()
            parent.remove(elem)
            if DEBUG==True: print(etree.tounicode(elem))
            elem = nxt
        if elem == end_elem:
            if delete_end==True:
                cls.remove(end_elem, leave_tail=True)
        elif elem is None:
            if parent.tail not in [None, '']:
                parent.tail = ''
            cls.remove_range(parent.getnext(), end_elem)
            XML.remove_if_empty(parent)
        elif end_elem in elem.xpath("descendant::*"):
            if DEBUG==True: print(elem.text)
            elem.text = ''
            cls.remove_range(elem.getchildren()[0], end_elem)
            XML.remove_if_empty(elem)
        else:
            print("LOGIC ERROR", file=sys.stderr)

    @classmethod
    def wrap_content(cls, container, wrapper):
        "wrap the content of container element with wrapper element"
        wrapper.text = (container.text or '') + (wrapper.text or '')
        container.text = ''
        for ch in container: wrapper.append(ch)
        container.insert(0, wrapper)
        return container

    @classmethod
    def tag_words_in(cls, elem, tag='w'):
        w = Dict(
            PATTERN = re.compile("([^\s]+)"),
            REPLACE = r'{%s}\1{/%s}' % (tag, tag),
            OMIT_ELEMS = [])
        def tag_words(e):
            e.text = re.sub(w.PATTERN, w.REPLACE, e.text or '')
            for ch in e:
                if ch.tag not in w.OMIT_ELEMS:
                    tag_words(ch)
                ch.tail = re.sub(w.PATTERN, w.REPLACE, ch.tail or '')
        new_elem = XML.fromstring(etree.tounicode(elem))
        tag_words(new_elem)
        s = etree.tounicode(new_elem)
        s = s.replace('{%s}' %tag, '<%s>' %tag).replace('{/%s}' %tag, '</%s>' %tag)
        new_elem = XML.fromstring(s)
        return new_elem

    @classmethod
    def merge_contiguous(C, node, xpath, namespaces=None):
        """Within a given node, merge elements that are next to each other 
        if they have the same tag and attributes.
        """
        new_node = deepcopy(node)
        elems = XML.xpath(new_node, xpath, namespaces=namespaces)
        elems.reverse()
        for elem in elems:
            next = elem.getnext()
            if elem.attrib == {}: 
                XML.replace_with_contents(elem)
            elif elem.tail in [None, ''] and next is not None \
            and elem.tag==next.tag and elem.attrib==next.attrib:
                # merge next with elem
                # -- append next.text to elem last child tail
                if len(elem.getchildren()) > 0:
                    lastch = elem.getchildren()[-1]
                    lastch.tail = (lastch.tail or '') + (next.text or '')
                else:
                    elem.text = (elem.text or '') + (next.text or '')
                # -- append next children to elem children
                for ch in next.getchildren():
                    elem.append(ch)
                # -- remove next
                XML.remove(next, leave_tail=True)
        return new_node

    # == Nesting Manipulations == 

    @classmethod
    def unnest(c, elem, ignore_whitespace=False):
        """unnest the element from its parent within doc. MUTABLE CHANGES"""
        parent = elem.getparent()
        gparent = parent.getparent()
        index = parent.index(elem)
        # put everything up to elem into a new parent element right before the current parent 
        preparent = etree.Element(parent.tag)
        preparent.text, parent.text = (parent.text or ''), ''
        for k in parent.attrib.keys(): 
            preparent.set(k, parent.get(k))
        if index > 0:
            for ch in parent.getchildren()[:index]:
                preparent.append(ch)
        gparent.insert(gparent.index(parent), preparent)
        XML.remove_if_empty(preparent, leave_tail=True, ignore_whitespace=ignore_whitespace)
        # put the element right before the current parent
        XML.remove(elem, leave_tail=True)
        gparent.insert(gparent.index(parent), elem)
        elem.tail = ''
        # if the original parent is empty, remove it
        XML.remove_if_empty(parent, leave_tail=True, ignore_whitespace=ignore_whitespace)

    @classmethod
    def interior_nesting(cls, elem1, xpath, namespaces=None):
        """for elem1 containing elements at xpath, embed elem1 inside each of those elements,
        and then remove the original elem1"""
        for elem2 in elem1.xpath(xpath, namespaces=namespaces):
            child_elem1 = etree.Element(elem1.tag)
            for k in elem1.attrib: child_elem1.set(k, elem1.get(k))
            child_elem1.text, elem2.text = elem2.text, ''
            for ch in elem2.getchildren(): child_elem1.append(ch)
            elem2.insert(0, child_elem1)
        XML.replace_with_contents(elem1)

    @classmethod
    def fragment_nesting(cls, elem1, tag2, namespaces=None):
        """for elem1 containing elements with tag2, 
        fragment elem1 into elems that are adjacent to and nested within tag2"""
        elems2 = elem1.xpath("child::%s" % tag2, namespaces=namespaces)
        while len(elems2) > 0:
            elem2 = elems2[0]
            parent2 = elem2.getparent()
            index2 = parent2.index(elem2)

            # all of elem2 has a new tag1 element embedded inside of it
            child_elem1 = etree.Element(elem1.tag)
            for k in elem1.attrib: child_elem1.set(k, elem1.get(k))
            elem2.text, child_elem1.text = '', elem2.text
            for ch in elem2.getchildren():
                child_elem1.append(ch)
            elem2.insert(0, child_elem1)

            # new_elem1 for all following children of parent2
            new_elem1 = etree.Element(elem1.tag)
            for k in elem1.attrib: new_elem1.set(k, elem1.get(k))
            new_elem1.text, elem2.tail = elem2.tail, ''
            for ch in parent2.getchildren()[index2+1:]:
                new_elem1.append(ch)

            # elem2 is placed after parent2
            parent = parent2.getparent()
            parent.insert(parent.index(parent2)+1, elem2)
            last_child = elem2

            # new_elem1 is placed after elem2
            parent.insert(parent.index(elem2)+1, new_elem1)
            new_elem1.tail, elem1.tail = elem1.tail, ''

            XML.remove_if_empty(elem1)
            XML.remove_if_empty(new_elem1)

            # repeat until all tag2 elements are unpacked from the new_elem1
            elem1 = new_elem1
            elems2 = elem1.xpath("child::%s" % tag2, namespaces=namespaces)

