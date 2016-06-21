from terrapin.parser import Parser

parser = Parser()


def render_full(template, context):
    """ Render with fully featured template engine """

    return parser.parse(template, context)