from terrapin.parser import Parser


def render(template, context):

    return Parser().parse(template, context)
