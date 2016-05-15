from collections import namedtuple
from .attributes import TransmuteAttributes
from ..compat import getfullargspec


class Parameters(object):
    def __init__(self, query=None, body=None, header=None, path=None, default_args=None, default_kwargs=None):
        self.query = query or {}
        self.body = body or {}
        self.header = header or {}
        self.path = path or {}
        self.default_args = {}
        self.default_kwargs = {}


def get_parameters(signature, transmute_attrs=None):
    """given a function, categorize which arguments should be passed by
    what types of parameters. The choices are:

    * query parameters: passed in as query parameters in the url
    * body parameters: retrieved from the request body (includes forms)
    * header parameters: retrieved from the request header
    * path parameters: retrieved from the uri path
    * default_args parameters: uncategorized positional arguments
    * default_kwargs parameters: uncategorized keyword arguments
    """
    params = Parameters()
    used_keys = set()
    # examine what variables are categorized first.
    for key in ["query", "body", "header", "path"]:
        explicit_parameters = getattr(transmute_attrs, key + "_parameters")
        for name in explicit_parameters:
            getattr(params, key)[name] = signature.get_argument(name)
            used_keys.add(name)

    # parse all positional params
    for arg in signature.args:
        if arg.name in used_keys:
            continue
        used_keys.add(name)
        params.default_args[arg.name] = arg

    for name, arg in signature.kwargs.items():
        if name in used_keys:
            continue
        used_keys.add(name)
        params.default_kwargs[name] = arg

    return params


class NoDefault(object):

    def __str__(self):
        return "NoDefault"

    def __repr__(self):
        return "NoDefault"

NoDefault = NoDefault()


Argument = namedtuple("Argument", ["name", "default", "type"])


class FunctionSignature(object):

    NoDefault = NoDefault

    def __init__(self, args, kwargs):
        self.args = args
        self.kwargs = kwargs

    def get_argument(self, key):
        if key in self.kwargs:
            return self.kwargs[key]
        for arg in self.args:
            if arg.name == key:
                return key

    @staticmethod
    def from_argspec(argspec):
        """
        retrieve a FunctionSignature object
        from the argspec and the annotations passed.
        """
        attributes = (getattr(argspec, "args", []) +
                      getattr(argspec, "keywords", []))
        defaults = argspec.defaults or []

        arguments, keywords = [], {}

        attribute_list = (attributes[:-len(defaults)]
                          if len(defaults) != 0
                          else attributes[:])
        for name in attribute_list:
            if name == "self":
                continue
            typ = argspec.annotations.get(name)
            arguments.append(Argument(name, NoDefault, typ))

        if len(defaults) != 0:
            for name, default in zip(attributes[-len(defaults):], defaults):
                typ = argspec.annotations.get(name)
                keywords[name] = Argument(name, default, typ)

        return FunctionSignature(arguments, keywords)
