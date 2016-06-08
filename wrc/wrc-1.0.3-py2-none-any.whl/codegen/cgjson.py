import re
import json
from wrc.sema.ast import WCADocument
from wrc.codegen.cg import CGDocument
from wrc.codegen.cghtml import simple_md2html

REGULATIONS_ROOT = "https://www.worldcubeassociation.org/regulations/"


class WCADocumentJSON(CGDocument):
    def __init__(self):
        super(WCADocumentJSON, self).__init__()
        self.reglist = []
        # This CG can handle both
        self.doctype = WCADocument

    def emit(self, regulations, guidelines):
        # FIXME: this override a function with a different number of arguments,
        # this is bad
        retval = self.visit(regulations) and self.visit(guidelines)
        return json.dumps(self.reglist)


    def visitRule(self, reg):
        self.reglist.append({'class': 'regulation', 'number': reg.number,
                             'text': simple_md2html(reg.text, REGULATIONS_ROOT)})
        retval = super(WCADocumentJSON, self).visitRule(reg)
        return retval

