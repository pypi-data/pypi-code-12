
import lxml.builder
from bl.dict import Dict

from .element_maker import ElementMaker

class Builder(Dict):
    """create a set of ElementMaker methods all bound to the same object."""
    def __init__(self, default=None, nsmap=None, **namespaces):
        Dict.__init__(self)
        for k in namespaces:        # each namespace gets its own method, named k (for each k)
            kdefault = default or namespaces[k]
            if nsmap is None:
                knsmap = {None:kdefault}
                knsmap.update(**{km:namespaces[km] for km in namespaces if namespaces[km]!=kdefault})
            self[k] = ElementMaker(namespace=namespaces[k], nsmap=nsmap or knsmap)
        if default is not None:
            # create an ElementMaker that uses the given namespace as the default
            if nsmap is None:
                knsmap = {None:default}
                knsmap.update(**{km:namespaces[km] for km in namespaces if namespaces[km]!=default})            
            self._ = ElementMaker(namespace=default, nsmap=nsmap or knsmap)
        else:
            # make elements with no namespace by default
            self._ = ElementMaker() 

    @classmethod
    def single(C, namespace):
        """An element maker with a single namespace that uses that namespace as the default"""
        return C(default=namespace)._
