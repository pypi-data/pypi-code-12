
import lxml.builder

class ElementMaker(lxml.builder.ElementMaker):
    """Our ElementMaker unpacks lists when it is called, enabling it to work with 
    nested-list-returning transformations using .xt.XT
    """
    
    def __call__(self, tag, *children, **attrib):
        chs = []
        for ch in children:
            if type(ch)==list:
                chs += [c for c in ch]
            elif ch is not None:
                chs.append(ch)
        return lxml.builder.ElementMaker.__call__(self, tag, *chs, **attrib)

