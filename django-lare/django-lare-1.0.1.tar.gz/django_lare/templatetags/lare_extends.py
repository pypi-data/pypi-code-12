from django.conf import settings
from django.template.base import TemplateSyntaxError, FilterExpression
from django.template import Library
from django.template.loader import get_template  # import to solve ImportErrors
from django.template.loader_tags import ExtendsNode

register = Library()


class LareExtendsNode(ExtendsNode):
    def __init__(self, nodelist, parent_name, lare_namespace, lare_template, template_dirs=None):
        super(LareExtendsNode, self).__init__(nodelist, parent_name, template_dirs=template_dirs)
        self.lare_namespace = lare_namespace
        self.lare_template = lare_template

    def __repr__(self):
        return '<LareExtendsNode: extends %s>' % self.parent_name.token

    def get_parent(self, context):
        lare_context = dict((k, v) for d in context.dicts for k, v in d.items() if (k == 'lare'))
        lare = lare_context.get('lare', False)
        if lare and lare.is_enabled() and lare.matches(self.lare_namespace.resolve(context)):
                self.parent_name = self.lare_template
            # try:
            #     namespace = lare.get_current_namspace()
            # except KeyError:
            #     pass  # no namespace given, so do not change parent_name => initial request
            # else:
            #     if namespace.startswith(self.lare_namespace.resolve(context)):
            #         self.parent_name = self.lare_template

        return super(LareExtendsNode, self).get_parent(context)


@register.tag()
def lare_extends(parser, token):
    bits = token.split_contents()
    if len(bits) != 4 and len(bits) != 3 and len(bits) != 2:
        raise TemplateSyntaxError("'%s' takes 1 - 3 arguments" % bits[0])

    nodelist = parser.parse()

    if nodelist.get_nodes_by_type(LareExtendsNode) or nodelist.get_nodes_by_type(ExtendsNode):
        raise TemplateSyntaxError("'lare_extends' and 'extends' cannot appear more than once in the same template!")

    if len(bits) > 2:
        try:
            # format DEFAULT_LARE_TEMPLATE string to fit into FilterExpression as token
            lare_template = parser.compile_filter(bits[3]) if (len(bits) == 4) else FilterExpression("'{0}'".format(settings.DEFAULT_LARE_TEMPLATE), parser)
        except AttributeError:
            raise TemplateSyntaxError("No lare template set, even no default!")
        return LareExtendsNode(nodelist, parser.compile_filter(bits[1]), parser.compile_filter(bits[2]), lare_template)
    return ExtendsNode(nodelist, parser.compile_filter(bits[1]))
