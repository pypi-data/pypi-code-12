
DEBUG = False

from lxml import etree, cssselect
from bf.text import Text

class CSS(Text):

    def __init__(self, **args):
        Text.__init__(self, **args)

    @classmethod
    def selector_to_xpath(cls, selector, xmlns=None):
        """convert a css selector into an xpath expression. 
        xmlns is option single-item dict with namespace prefix and href"""

        selector = selector.replace(' .', ' *.')
        if selector[0] == '.':
            selector = '*' + selector
            if DEBUG==True: print('', selector)
        
        if '#' in selector:
            selector = selector.replace('#', '*#')
            if DEBUG==True: print('', selector)

        if xmlns is not None:
            prefix = xmlns.keys()[0]
            href = xmlns[prefix]
            selector = ' '.join([
                (n.strip() != '>' and prefix + '|' + n.strip() or n.strip())
                for n in selector.split(' ')
                ])
            if DEBUG==True: print('', selector)
        
        path = cssselect.CSSSelector(selector, namespaces=xmlns).path
        path = path.replace("descendant-or-self::", "")
        path = path.replace("/descendant::", "//")
        
        if DEBUG==True: print(' ==>', path)
        
        return path

    # **NOTE: This procedure from the cssutils based version of this class will not work as-is**
    # 
    # def add_selectors_from(self, cssfns, verbose=False):
    #     """add any selectors from cssfn that are missing in this CSS file -- append to the end"""
    #     if type(cssfns) in [str, unicode]:
    #         cssfns = [cssfns]
    #     elif type(cssfns) != list:
    #         raise TypeError('invalid type for cssfns parameter:' + str(type(cssfns)))

    #     self_rules = [r for r in self.doc.cssRules if r.typeString=='STYLE_RULE']
    #     self_selectors = []
    #     for rule in self_rules:
    #         for sel in rule.selectorList:
    #             if sel.selectorText not in self_selectors: self_selectors.append(sel.selectorText)

    #     for cssfn in cssfns:
    #         if verbose==True: print(cssfn)
    #         css = CSS(cssfn)
    #         css_rules = [r for r in css.doc.cssRules if r.typeString=='STYLE_RULE']
    #         css_selectors = []
    #         for rule in css_rules:
    #             for sel in rule.selectorList:
    #                 if sel.selectorText not in css_selectors: css_selectors.append(sel.selectorText)
    #         for sel in [sel for sel in css_selectors if sel not in self_selectors]:
    #             new_rule = cssutils.css.CSSStyleRule(selectorText=sel, style=rule.style)
    #             self.doc.cssRules.append(new_rule)
    #             self_rules.append(new_rule)
    #             self_selectors.append(sel)
    #             if verbose==True: print(' ', sel)
