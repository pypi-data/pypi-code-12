
from copy import deepcopy
from lxml import etree
from bl.dict import Dict
from bl.log import Log

def match(xt, expression=None, xpath=None, namespaces=None): 
    """decorator that allows us to match by expression or by xpath for each transformation method"""
    class MatchObject(Dict):
        pass
    def _match(function):
        xt.matches.append(
            MatchObject(expression=expression, xpath=xpath, function=function, namespaces=namespaces))
        def wrapper(self, *args, **params):
            return function(self, *args, **params)
        return wrapper
    return _match

class XT:
    """XML Transformations (XT)"""

    def __init__(self, debug=False, log=Log()):
        # a list of matches to select which transformation method to apply
        self.matches = []
        self.debug = debug
        self.log = log

    def __call__(self, elems, mutable={}, **params):
        """provide a consistent interface for transformations"""
        ee = [] 
        if type(elems) != list:
            elems = [elems]
        for elem in elems:
            if self.debug==True: self.log(elem)
            if type(elem)==str:
                ee.append(elem)
            else:
                for m in self.matches:
                    if (m.expression is not None and eval(m.expression)==True) \
                    or (m.xpath is not None and len(elem.xpath(m.xpath, namespaces=m.namespaces)) > 0):
                        if self.debug==True: self.log("=> match:", expression)
                        ee += m.function(elem, mutable=mutable, **params)
                        break
        return ee

    def Element(self, elem, mutable={}, **params):
        """Ensure that the input element is immutable by the transformation. Returns a single element."""
        res = self.__call__(deepcopy(elem), mutable=mutable, **params)
        if len(res) > 0: 
            return res[0]
        else:
            return None

    # == COMMON TRANSFORMATION METHODS ==

    def inner_xml(self, elem, with_tail=True, mutable={}, **params):
        x = [elem.text or ''] \
            + self(elem.getchildren(), mutable=mutable, **params)
        if with_tail == True:
            x += [elem.tail or '']
        return x

    def omit(self, elem, keep_tail=True, mutable={}, **params):
        r = []
        if keep_tail == True and elem.tail is not None:
            r += [elem.tail]
        return r

    def copy(self, elem, mutable={}, **params):
        return deepcopy(elem)

