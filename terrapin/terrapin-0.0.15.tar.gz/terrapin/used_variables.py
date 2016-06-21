from terrapin.parser import Parser

parser = Parser()


class ObservingContext(dict):
    """ Keep a record of which keys have tried to be accessed """

    def __init__(self, *args, **kwargs):

        self.keys_seen = set()

    def get(self, key, *args, **kwargs):

        self.keys_seen.add(key)
        return super(ObservingContext, self).get(key, *args, **kwargs)


def used_variables(template):
    """ Return a set of used variables in the template """

    context = ObservingContext()
    parser.parse(template, context)
    return context.keys_seen
