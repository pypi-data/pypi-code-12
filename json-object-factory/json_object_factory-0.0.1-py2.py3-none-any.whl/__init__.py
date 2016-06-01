import json

from jsonfactory.registry import Registry
from jsonfactory.decorators import register, encoder, decoder

class Encoder(json.JSONEncoder):
    def default(self, o):
        r = Registry.encode(o)
        if r is not None:
            return r
        return super(Encoder, self).default(o)

def obj_hook(d):
    return Registry.decode(d)

def dumps(obj, **kwargs):
    kwargs.setdefault('cls', Encoder)
    return json.dumps(obj, **kwargs)

def loads(s, **kwargs):
    kwargs.setdefault('object_hook', obj_hook)
    return json.loads(s, **kwargs)
