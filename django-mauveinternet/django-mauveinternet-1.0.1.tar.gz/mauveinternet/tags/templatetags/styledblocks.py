from django.template import Node, Library, resolve_variable, TemplateSyntaxError, loader
from django.conf import settings
from django.utils.safestring import mark_safe
from django.template.loader_tags import ExtendsNode, BlockNode

register = Library()

class WrapWithNode(Node):
    """Includes another template to style the contents of this tag.

    This is similar to {% include %}, except that it takes tag
    contents which are rendered and passed to the included template
    as an additional variable {{ wrapped }}.

    """
    def __init__(self, template_name, nodelist):
        self.nodelist = nodelist
        self.template_name = template_name

    def render(self, context):
        t = loader.get_template(self.template_name)
        wrapped = self.nodelist.render(context)
        context.update({'wrapped': mark_safe(wrapped)})
        output = t.render(context)
        context.pop()
        return output


@register.tag
def wrapwith(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        name, template_name = token.split_contents()
    except ValueError:
        raise TemplateSyntaxError, "%r tag requires exactly one arguments" % name

    nodelist = parser.parse(('endwrapwith',))
    parser.delete_first_token()     # consume {% endwrapwith %} tag

    return WrapWithNode(template_name[1:-1], nodelist)


class CallNode(Node):
    def __init__(self, nodelist, template_name):
        self.delegate = ExtendsNode(nodelist, template_name, None)

    def render(self, context):
        return self.delegate.render(context)

@register.tag()
def call(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        name, template_name = token.split_contents()
    except ValueError:
        raise TemplateSyntaxError, "%r tag requires exactly one arguments" % name

    try:
        seen_blocks = parser.__loaded_blocks
        del(parser.__loaded_blocks)
    except AttributeError:
        nodelist = parser.parse(('endcall',))
    else:
        nodelist = parser.parse(('endcall',))
        parser.__loaded_blocks = seen_blocks
    parser.delete_first_token()     # consume {% endwrapwith %} tag
    return CallNode(nodelist, template_name[1:-1])


@register.tag(name='b')
def do_block(parser, token):
    """Shortcut alias for {% block %} tag."""

    bits = token.contents.split()
    if len(bits) != 2:
        raise TemplateSyntaxError, "'%s' tag takes only one argument" % bits[0]
    block_name = bits[1]
    # Keep track of the names of BlockNodes found in this template, so we can
    # check for duplication.
    try:
        if block_name in parser.__loaded_blocks:
            raise TemplateSyntaxError, "'%s' tag with name '%s' appears more than once" % (bits[0], block_name)
        parser.__loaded_blocks.append(block_name)
    except AttributeError: # parser.__loaded_blocks isn't a list yet
        parser.__loaded_blocks = [block_name]
    nodelist = parser.parse(('endb', 'endb %s' % block_name))
    parser.delete_first_token()
    return BlockNode(block_name, nodelist)
