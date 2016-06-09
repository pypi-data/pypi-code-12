
import time
from lxml import etree
from bl.dict import Dict
from bl.string import String

from .xml import XML

XSL_NAMESPACE = "xmlns:xsl='http://www.w3.org/1999/XSL/Transform'"
XSL_TEMPLATE = """<xsl:stylesheet version="1.0" %s%s><xsl:output method="xml"/></xsl:stylesheet>"""

class XSLT(XML):
    """class for holding, manipulating, and using XSL documents"""

    TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S %Z"       # format for timestamp params

    CACHE = Dict()              # XSLT.CACHE = application-level cache. 
                                # The keys are digests of the XSLT text, which ensures that 
                                # unchanged xslt will cache, while changed xslt will compile.
    
    def __init__(self, cache=True, **kwargs):
        XML.__init__(self, **kwargs)
        self.xslt = self.make_xslt(cache=cache)
        
    def __call__(self, elem, **params):
        # prepare string parameters -- see http://lxml.de/xpathxslt.html#stylesheet-parameters
        if 'timestamp' not in params.keys():     # always include a timestamp param
            params['timestamp'] = time.strftime(self.TIMESTAMP_FORMAT)
        for key in params:
            if type(params[key]) in [str, bytes]:
                params[key] = etree.XSLT.strparam(params[key])
        return self.xslt(elem, **params)
    
    def append(self, s, *args):
        if type(s) == etree._Element:
            elem = s
        else:
            elem = XML.Element(s, *args)
        try:
            self.root.append(elem)
            self.xslt = self.make_xslt()
        except:
            self.root.remove(elem)
            raise

    def make_xslt(self, elem=None, cache=True):
        # parse the source file here if available, so that the XSLT knows where it is.
        if elem is None: 
            if self.fn is not None:
                elem = etree.parse(self.fn)
            else:
                elem = self.root
        if cache==True:
            digest = String(etree.tounicode(elem)).digest()
            if self.__class__.CACHE.get(digest) is not None:
                return self.__class__.CACHE.get(digest)
            xsl = self.__class__.CACHE[digest] = etree.XSLT(elem)
        else:
            xsl = etree.XSLT(elem)
        return xsl

    @classmethod
    def clear_cache(self):
        XSLT.CACHE = Dict()

    # == TEMPLATE METHODS == 
    
    @classmethod
    def stylesheet(cls, *args, namespaces=None):
        if namespaces is not None:
            nst = ' ' + ' '.join(["xmlns:%s='%s'" % (k, namespaces[k]) for k in namespaces.keys()])
        else:
            nst = ''
        xt = XML.Element(XSL_TEMPLATE % (XSL_NAMESPACE, nst))
        for arg in args:
            xt.append(XML.Element(arg))
        return xt

    @classmethod
    def copy_all(cls):
        return XML.Element(
            """<xsl:template match="@*|node()" %s><xsl:copy><xsl:apply-templates select="@*|node()"/></xsl:copy></xsl:template>""", 
            XSL_NAMESPACE)

    @classmethod
    def copy(cls, val):
        return XML.Element("""<xsl:copy %s>%s</xsl:copy>""", XSL_NAMESPACE, val)

    @classmethod
    def copy_select(cls, select, val):
        return XML.Element("""<xsl:copy %s select="%s">%s</xsl:copy>""", XSL_NAMESPACE, select, val)

    @classmethod
    def copy_of(cls):
        return XML.Element("""<xsl:copy-of %s/>""", XSL_NAMESPACE)

    @classmethod
    def copy_of_select(cls, select):
        return XML.Element("""<xsl:copy-of %s select="%s"/>""", XSL_NAMESPACE, select)

    @classmethod
    def choose(cls, *args):
        return XML.Element("<xsl:choose %s/>", XSL_NAMESPACE, *args)

    @classmethod
    def when(cls, test, val):
        return XML.Element("""<xsl:when %s test="%s">%s</xsl:when>""", XSL_NAMESPACE, test, val)

    def otherwise(cls, val):
        return XML.Element("""<xsl:otherwise %s>%s</xsl:otherwise>""", XSL_NAMESPACE, test, val)

    @classmethod
    def template_match(cls, match, val):
        return XML.Element("""<xsl:template %s match="%s">%s</xsl:template>""", 
            XSL_NAMESPACE, match, val)

    @classmethod
    def template_match_mode(cls, match, mode, val):
        return XML.Element("""\n<xsl:template %s match="%s" mode="%s">%s</xsl:template>""", 
            XSL_NAMESPACE, match, mode, val)
                
    @classmethod
    def template_name(cls, name, val):
        return XML.Element("""<xsl:template %s name="%s">%s</xsl:template>""", 
            XSL_NAMESPACE, name, val)

    @classmethod
    def template_match_omission(cls, match):
        return XML.Element("""<xsl:template %s match="%s"/>""", XSL_NAMESPACE, match)

    @classmethod
    def apply_templates(cls):
        return XML.Element("""<xsl:apply-templates %s/>""", XSL_NAMESPACE)

    @classmethod
    def apply_templates_mode(cls, mode):
        return XML.Element("""<xsl:apply-templates %s mode="%s"/>""", XSL_NAMESPACE, mode)

    @classmethod
    def apply_templates_select(cls, select):
        return XML.Element("""<xsl:apply-templates %s select="%s"/>""", XSL_NAMESPACE, select)

    @classmethod
    def apply_templates_select_mode(cls, select, mode):
        return XML.Element("""<xsl:apply-templates %s select="%s" mode="%s"/>""", 
            XSL_NAMESPACE, select, mode)

    @classmethod
    def element(cls, name, val):
        return XML.Element("""<xsl:element %s name="%s">%s</xsl:element>""", 
            XSL_NAMESPACE, name, val)
        
    @classmethod
    def attribute(cls, name, val):
        return XML.Element("""<xsl:attribute %s name="%s">%s</xsl:attribute>""", 
            XSL_NAMESPACE, name, val)

    @classmethod
    def variable(cls, name, val):
        return XML.Element("""<xsl:variable %s name="%s">%s</xsl:variable>""", 
            XSL_NAMESPACE, name, val)

    @classmethod
    def variable_select(cls, name, select):
        return XML.Element("""<xsl:variable %s name="%s" select="%s"/>""", 
            XSL_NAMESPACE, name, select)

    @classmethod
    def value_of(cls, select):
        return XML.Element("""<xsl:value-of %s select="%s"/>""", XSL_NAMESPACE, select)

    @classmethod
    def text(cls, t):
        return XML.Element("""<xsl:text %s>%s</xsl:text>""", XSL_NAMESPACE, t)

    @classmethod
    def for_each(cls, select, val):
        return XML.Element("""<xsl:for-each %s select="%s">%s</xsl:for-each>""", 
            XSL_NAMESPACE, select, val)

    @classmethod
    def if_test(cls, test, val):
        return XML.Element("""<xsl:if %s test="%s">%s</xsl:if>""", XSL_NAMESPACE, test, val)

    @classmethod
    def output_method(cls, method):
        return XML.Element("""<xsl:output method="%s" encoding="utf-8" %s/>""", 
            XSL_NAMESPACE, method)

    # -- STILL TO ADD: -- 
    # xsl:output, xsl:include, xsl:copy, xsl:copy-of, xsl:param, 
    # xsl:apply-templates select|match, xsl:call-template

# XPATH FUNCTIONS
def uppercase(context, elems):
    for elem in elems:
        if type(elem)==etree._ElementUnicodeResult:
            elem = elem.upper()
        else:
            elem.text = elem.text.upper()
            for ch in elem.getchildren():
                uppercase(cls, [ch])
                ch.tail = (ch.tail or '').upper()
    return elems

def lowercase(context, elems):
    for elem in elems:
        if type(elem)==etree._ElementUnicodeResult:
            elem = elem.lower()
        else:
            elem.text = elem.text.lower()
            for ch in elem.getchildren():
                lowercase(cls, [ch])
                ch.tail = (ch.tail or '').lower()
    return elems

def register_xpath_functions(functions=[], namespace=None):
    ns = etree.FunctionNamespace(namespace)
    for fn in functions:
        ns[fn.__name__] = fn

register_xpath_functions([uppercase, lowercase])

