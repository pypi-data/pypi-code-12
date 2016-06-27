# DOCX object class

DEBUG = False

import os, re, tempfile
from lxml import etree

from bl.dict import Dict
from bl.string import String
from bl.zip import ZIP
from bxml.xml import XML
from bf.text import Text

class DOCX(ZIP):
    NS = Dict(**{
        # document namespaces, in word/*.xml
        'wpc': "http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas",
        'mc':  "http://schemas.openxmlformats.org/markup-compatibility/2006",
        'o':   "urn:schemas-microsoft-com:office:office",
        'r':   "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
        'm':   "http://schemas.openxmlformats.org/officeDocument/2006/math",
        'v':   "urn:schemas-microsoft-com:vml",
        'wp14':"http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing",
        'wp':  "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
        'w10': "urn:schemas-microsoft-com:office:word",
        'w':   "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
        'w14': "http://schemas.microsoft.com/office/word/2010/wordml",
        'w15': "http://schemas.microsoft.com/office/word/2012/wordml",
        'wpg': "http://schemas.microsoft.com/office/word/2010/wordprocessingGroup",
        'wpi': "http://schemas.microsoft.com/office/word/2010/wordprocessingInk",
        'wne': "http://schemas.microsoft.com/office/word/2006/wordml",
        'wps': "http://schemas.microsoft.com/office/word/2010/wordprocessingShape",

        # metadata namespaces, in docProps/core.xml
        'dc':     "http://purl.org/dc/elements/1.1/",
        'dcterms':"http://purl.org/dc/terms/", 
        'dcmitype':"http://purl.org/dc/dcmitype/", 
        'cp':     "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",

        # other namespaces, such as in word/_rels
        'rels':  "http://schemas.openxmlformats.org/package/2006/relationships",

        # xhtml namespace needed here for certain uses.
        'html': "http://www.w3.org/1999/xhtml",
    })

    def tempfile(self):
        "write the docx to a named tmpfile and return the tmpfile filename"
        tf = tempfile.NamedTemporaryFile()
        tfn = tf.name
        tf.close()
        os.remove(tf.name)
        shutil.copy(self.fn, tfn)
        return tfn

    def write(self, fn=None):
        fn = fn or self.fn
        if not os.path.exists(os.path.dirname(fn)):
            os.makedirs(os.path.dirname(fn))
        f = open(self.fn, 'rb'); b = f.read(); f.close()
        f = open(fn, 'wb'); f.write(b); f.close()

    def transform(self, transformer, fn=None, XMLClass=None, **params):
        return self.xml(fn=fn, transformer=transformer, XMLClass=XMLClass, **params)

    def read(self, src):
        """return file data from within the docx file"""
        return self.zipfile.read(src)

    def xml(self, fn=None, src='word/document.xml', transformer=None, XMLClass=None, **params):
        "return the src with the given transformation applied, if any."
        if src not in self.zipfile.namelist(): return
        XMLClass = XMLClass or XML
        x = XMLClass(fn=fn or (self.fn and self.fn.replace('.docx', '.xml')) or None, # possibly there is none
                root=self.zipfile.open(src).read(),
                config=self.config)
        if transformer is not None:
            x = XMLClass(fn=x.fn, 
                    root=transformer.Element(x.root, docx=self, fn=x.fn, **params), 
                    config=x.config)
        if DEBUG == True:
            t = etree.tounicode(x.root, pretty_print=False)
            td = Text(fn=self.fn + '-' + src.replace('/','_')+".txt")
            td.text = t
            td.write()
            print("DEBUG:", td.fn)
            x = XMLClass(fn=x.fn, 
                    root=etree.fromstring(t), 
                    config=x.config)
        return x

    def metadata(self):
        """return a cp:metadata element with the metadata in the document"""
        xml = self.xml(src="docProps/core.xml")
        return xml.root

    def stylemap(self, definitions=True, all=True, cache=False):
        """return a dictionary of styles from .docx word/styles.xml, keyed to the id
        (the id is used in the .docx word/document.xml rather than the style names; 
        this method creates a mapping for us to use when outputting the document).
        if definitions==True (default), then style definitions are also included.
        if all==False, then only those styles that are used are included (slower).
        """
        if self._stylemap is not None and cache==True:
            return self._stylemap
        else:
            self._stylemap = None              # expire the cache
            x = self.xml(src='word/styles.xml')
            document = self.xml(src='word/document.xml')
            footnotes = self.xml(src='word/footnotes.xml')  # None if no footnotes
            endnotes = self.xml(src='word/endnotes.xml')    # None if no endnotes
            d = Dict()
            for s in x.root.xpath("w:style", namespaces=self.NS):
                style = Dict()
                style.id = s.get("{%(w)s}styleId" % self.NS)
                style.type = s.get("{%(w)s}type" % self.NS)
                style.xpath = "//w:rStyle[@w:val='%(id)s'] | //w:pStyle[@w:val='%(id)s']" % style
                if all == False:
                    uses = document.root.xpath(style.xpath, namespaces=DOCX.NS)
                    if len(uses)==0:
                        # try footnotes and endnotes
                        if footnotes is not None:
                            uses = footnotes.root.xpath(style.xpath, namespaces=DOCX.NS)
                        if len(uses)==0:
                            if endnotes is not None:
                                uses = endnotes.root.xpath(style.xpath, namespaces=DOCX.NS)
                            if len(uses)==0:
                                continue
                style.name = s.find("{%(w)s}name" % self.NS).get("{%(w)s}val" % self.NS)
                d[style.id] = style
                if definitions != True: 
                    continue
                bo = s.find("{%(w)s}basedOn" % DOCX.NS)
                if bo is not None:
                    style.basedOn = bo.get("{%(w)s}val" % DOCX.NS)
                style.properties = Dict()
                for pr in s.xpath("w:pPr/* | w:rPr/*", namespaces=DOCX.NS):
                    tag = re.sub("^\{[^}]*\}", "", pr.tag)
                    props = Dict()
                    for attr in pr.attrib.keys():
                        k = re.sub("^\{[^}]*\}", "", attr)
                        props[k] = pr.get(attr)
                    style.properties[tag] = props
            if cache==True: self._stylemap = d
            return d

    def endnotemap(self, cache=True):
        """return the endnotes from the docx, keyed to string id."""
        if self.__endnotemap is not None and cache==True:
            return self.__endnotemap
        else:
            x = self.xml(src='word/endnotes.xml')
            d = Dict()
            if x is None: return d
            for endnote in x.root.xpath("w:endnote", namespaces=self.NS):
                id = endnote.get("{%(w)s}id" % self.NS)
                typ = endnote.get("{%(w)s}type" % self.NS)
                d[id] = Dict(id=id, type=typ, elem=endnote)
            if cache==True: self.__endnotemap = d
            return d

    def footnotemap(self, cache=True):
        """return the footnotes from the docx, keyed to string id."""
        if self.__footnotemap is not None and cache==True:
            return self.__footnotemap
        else:
            x = self.xml(src='word/footnotes.xml')
            d = Dict()
            if x is None: return d
            for footnote in x.root.xpath("w:footnote", namespaces=self.NS):
                id = footnote.get("{%(w)s}id" % self.NS)
                typ = footnote.get("{%(w)s}type" % self.NS)
                d[id] = Dict(id=id, type=typ, elem=footnote)
            if cache==True: self.__footnotemap = d
            return d

    def commentmap(self, cache=True):
        """return the comments from the docx, keyed to string id."""
        if self.__commentmap is not None and cache==True:
            return self.__commentmap
        else:
            x = self.xml(src='word/comments.xml')
            d = Dict()
            if x is None: return d
            for comment in x.root.xpath("w:comment", namespaces=self.NS):
                id = comment.get("{%(w)s}id" % self.NS)
                typ = comment.get("{%(w)s}type" % self.NS)
                d[id] = Dict(id=id, type=typ, elem=comment)
            if cache==True: self.__commentmap = d
            return d

    def docvars(self, cache=True):
        if self.__docvars is not None and cache==True:
            return self.__docvars
        else:
            x = self.xml(src='word/settings.xml', braces_xml=False)
            d = Dict()
            for docvar in x.root.xpath("w:docVars/w:docVar", namespaces=self.NS):
                name = docvar.get("{%(w)s}name" % self.NS)
                val = docvar.get("{%(w)s}val" % self.NS)
                d[name] = val
            if cache==True: self.__docvars = d
            return d

    @classmethod
    def classname(C, stylename):
        "convert a Word stylename into an HTML/CSS class name"
        return String(stylename).nameify()

    @classmethod
    def strftime_string(C, msformat):
        "convert Word date/time picture (msformat) into a strftime format string"
        s = msformat
        s = re.sub("%", "%%", s)                   # percent sign
        s = re.sub(r"(?<!%)\b(y(?:yyy)?)\b", "%Y", s)   # 4-digit year
        s = re.sub(r"(?<!%)\b(yy)\b", "%y", s)     # 2-digit year
        s = re.sub(r"(?<!%)\b(MMMM)\b", "%B", s)   # full month
        s = re.sub(r"(?<!%)\b(MMM)\b", "%b", s)    # abbrev. month
        s = re.sub(r"(?<!%)\b(MM)\b", "%m", s)     # 2-digit month
        s = re.sub(r"(?<!%)\b(dd?)\b", "%d", s)    # day
        s = re.sub(r"(?<!%)\b(hh?)\b", "%I", s)    # 12-hr hour
        s = re.sub(r"(?<!%)\b(HH?)\b", "%H", s)    # 24-hr hour
        s = re.sub(r"(?<!%)\b(mm?)\b", "%M", s)    # minute
        s = re.sub(r"(?<!%)\b(ss?)\b", "%S", s)    # second
        s = re.sub(r"(?<!%)\b(am/pm)\b", "%p", s)  # 2-digit year
        return s

    @classmethod
    def value_to(C, val, unit, factor=1.):
        "converts a Word value to a given unit, using the factor given"
        from bl import scss
        val = float(val) * factor
        return round(float(val*scss.pt/unit), 2)*unit

    def stylesheet(self, fn=None, log=print):
        "create an SCSS stylesheet in a Text document, using DOCX.stylemap(), above."
        from bl import scss
        SPACE_PTS_FACTOR = 1/30.  # divide Word space values by 20 to get the number of points
        FONT_PTS_FACTOR = 1/2.    # divide Word font size values by 2 to get the number of points
        styles = self.stylemap(definitions=True, all=True, cache=False)
        all_styles = self.stylemap(all=False, cache=False)
        ss = scss.SCSS(fn=fn or (self.fn and self.fn.replace('.docx', '.scss')) or None)
        incl_styles = [i for i in styles.keys() if i in all_styles]
        for i in incl_styles:
            style = styles[i]
            if DEBUG==True: log(style.name)
            clas = self.classname(style.name)
            if style.type == 'paragraph':
                tag = 'p'
            elif style.type == 'character':
                tag = 'span'
            sel = tag + '.' + clas
            ss.styles[sel] = Dict()
            if style.basedOn is not None:
                ss.styles[sel]["@extend"] = tag + '.' + self.classname(styles[style.basedOn].name)
                # make sure all the "base" styles are included in the stylesheet
                if style.basedOn not in incl_styles:
                    incl_styles.append(style.basedOn)
            for j in style.properties.keys():
                prop = style.properties[j]
                if DEBUG==True: log('\t', prop)
                if j == 'spacing':
                    for k in prop.keys():
                        if k=='after': 
                            ss.styles[sel]["margin-bottom:"] = DOCX.value_to(prop[k], scss.pt, factor=SPACE_PTS_FACTOR)
                        elif k=='before': 
                            ss.styles[sel]["margin-top:"] = DOCX.value_to(prop[k], scss.pt, factor=SPACE_PTS_FACTOR)
                        elif k in ['beforeAutospacing', 'afterAutospacing']:
                            pass
                        elif k=='line':
                            ss.styles[sel]["line-spacing:"] = DOCX.value_to(prop[k], scss.pt, factor=SPACE_PTS_FACTOR)
                        elif k=='lineRule':
                            pass
                        else:
                            log(i, j, k, prop[k])
                elif j == 'jc':
                    for k in prop.keys():
                        if k=='val':
                            if prop[k] in ['center', 'right', 'left', 'justify']:
                                ss.styles[sel]["text-align:"] = "%s" % prop[k]
                            else:
                                log(i, j, k, prop[k])
                        else:
                            log(i, j, k, prop[k])
                elif j in ['sz', 'szCs']:
                    for k in prop.keys():
                        if k=='val':
                            ss.styles[sel]["font-size:"] = DOCX.value_to(prop[k], scss.pt, factor=FONT_PTS_FACTOR)
                        else:
                            log(i, j, k, prop[k])
                elif j=='rFonts':
                    f = prop.get('hAnsi') or prop.get('ascii')
                    if f is not None:
                        ss.styles[sel]["font-family:"] = '"%s"' % f
                elif j=='pBdr':
                    for k in prop.keys():
                        log(i, j, k, prop[k])
                elif j=='ind':
                    for k in prop.keys():
                        if k=='firstLine':
                            ss.styles[sel]["text-indent:"] = DOCX.value_to(prop[k], scss.pt, factor=SPACE_PTS_FACTOR)
                        elif k=='left':
                            if ss.styles[sel].get("margin-left:") is None:
                                ss.styles[sel]["margin-left:"] = 0*scss.pt
                            ss.styles[sel]["margin-left:"] += DOCX.value_to(prop[k], scss.pt, factor=SPACE_PTS_FACTOR)
                        elif k=='right':
                            ss.styles[sel]["margin-right:"] = DOCX.value_to(prop[k], scss.pt, factor=SPACE_PTS_FACTOR)
                        elif k=='hanging':
                            if ss.styles[sel].get("margin-left:") is None:
                                ss.styles[sel]["margin-left:"] = 0*scss.pt
                            ss.styles[sel]["margin-left:"] += DOCX.value_to(prop[k], scss.pt, factor=SPACE_PTS_FACTOR)
                            ss.styles[sel]["text-indent:"] = -DOCX.value_to(prop[k], scss.pt, factor=SPACE_PTS_FACTOR)
                        else:
                            log(i, j, k, prop[k])
                elif j in ['b', 'bCs']:
                    if prop.val=='0':
                        ss.styles[sel]["font-weight:"] = "normal"
                    else:
                        ss.styles[sel]["font-weight:"] = "bold"
                elif j in ['i', 'iCs']:
                    if prop.val=='0':
                        ss.styles[sel]["font-style:"] = "normal"
                    else:
                        ss.styles[sel]["font-style:"] = "italic"
                elif j=='smallCaps':
                    if prop.val=='0':
                        ss.styles[sel]["font-variant:"] = "normal"
                    else:
                        ss.styles[sel]["font-variant:"] = "small-caps"
                elif j=='caps' and prop.val!=0:
                    if ('smallCaps' not in style.properties.keys() 
                    or style.properties['smallCaps'].val==0):
                        ss.styles[sel]["text-transform:"] = "uppercase"
                elif j=='textAlignment':
                    if prop.val=='baseline':
                        ss.styles[sel]["vertical-align:"] = "baseline"
                    elif prop.val=='center':
                        ss.styles[sel]['text-align:'] = 'center'
                    else:
                        log(i, j, k, prop[k])
                elif j=='vertAlign':
                    if prop.val=='superscript':
                        ss.styles[sel]["vertical-align:"] = "text-top"
                        ss.styles[sel]["font-size:"] = "75%"
                    elif prop.val=='subscript':
                        ss.styles[sel]["vertical-align:"] = "text-bottom"
                        ss.styles[sel]["font-size:"] = "75%"
                    else:
                        log(i, j, prop)
                elif j=='vanish':
                    if prop.val=='1':
                        ss.styles[sel]["display:"] =  "none"
                    elif prop.val=='0':
                        if style.type=='paragraph':
                            ss.styles[sel]["display:"] = "block"
                        elif style.type=='character':
                            ss.styles[sel]["display:"] = "inline"
                        else:
                            log(i, j, prop)
                    else:
                        log(i, j, prop)
                elif j=='pageBreakBefore':
                    ss.styles[sel]["page-break-before:"] = "always"
                elif j=='keepNext':
                    ss.styles[sel]["page-break-after:"] = "avoid"
                elif j=='color':
                    if prop.val != 'auto':
                        ss.styles[sel]["color:"] = "#%s" % prop.val
                elif j in ['autoSpaceDN', 'autoSpaceDE', 'tabs', 'spacing', 'contextualSpacing',
                        'suppressLineNumbers', 'suppressAutoHyphens', 'overflowPunct',
                        'adjustRightInd', 'widowControl', 'outlineLvl', 'w',
                        'keepLines', 'lang', 'ligatures', 'numForm', 'numPr', 'numSpacing',]:
                    pass
                else:
                    log(i, j, prop)
        return ss