from collections import OrderedDict


class SwaggerMapping(OrderedDict):

    def __repr__(self):
        return repr(dict(self))


class ModelRef(str):
    pass
