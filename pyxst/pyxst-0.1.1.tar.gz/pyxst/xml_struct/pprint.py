import sys


class PrettyPrinter(object):
    def __init__(self, print_qname=True, indent='  '):
        self.print_qname = print_qname
        self.indent = indent

    def pprint(self, element, out=sys.stdout, indent=''):
        callback = getattr(self, 'visit_' + element.__class__.__name__.lower())
        callback(out, element, indent)

    def visit_xmlelement(self, out, element, indent):
        if self.print_qname:
            name = element.local_name
        else:
            name = "{%s}%s" % (element.namespace, element.local_name)
        out.write(indent + '<' + name + '>' + '\n')
        if element.content:
            self.pprint(element.content, out, indent + self.indent)

    def visit_occurence(self, out, element, indent):
        if element.minimum == element.maximum:
            occurs = u"[{0}]".format(element.minimum)
        else:
            occurs = u"[{0},{1}]".format(element.minimum, element.maximum)
        out.write(indent + occurs + '\n')
        self.pprint(element.target, out, indent + self.indent)

    def visit_group(self, out, element, indent):
        out.write(indent + element.__class__.__name__ + '\n')
        for occ in element.children:
            self.pprint(occ, out, indent + self.indent)

    visit_alternative = visit_sequence = visit_group
