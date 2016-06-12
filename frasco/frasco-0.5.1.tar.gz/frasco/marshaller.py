from flask import Response
from .utils import ContextStack, FlagContextStack, AttrDict
import functools


try:
    from marshmallow import Schema as MarshmallowSchema
    marshmallow_available = True
except ImportError:
    marshmallow_available = False


marshaller_context = FlagContextStack()
marshalling_context_stack = ContextStack()
marshalling_context = marshalling_context_stack.make_proxy()


def marshal(rv, marshaller, func=None, args=None, kwargs=None, **marshaller_kwargs):
    with marshalling_context_stack(AttrDict(func=func, args=args, kwargs=kwargs)):
        if marshmallow_available and issubclass(marshaller, MarshmallowSchema):
            schema = marshaller(**marshaller_kwargs)
            return schema.dump(rv).data
        elif hasattr(marshaller, '__marshaller__'):
            marshaller = marshaller.__marshaller__
        return marshaller(rv, **marshaller_kwargs)


def marshal_with(marshaller, **marshaller_kwargs):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _marshal = False
            if marshaller_context.top:
                marshaller_context.consume_once()
                _marshal = True
            rv = func(*args, **kwargs)
            if _marshal:
                return marshal(rv, marshaller, func=func, args=args, kwargs=kwargs, **marshaller_kwargs)
            return rv
        wrapper.marshalled_with = marshaller
        return wrapper
    return decorator


def marshal_many_with(marshaller, **marshaller_kwargs):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            items = func(*args, **kwargs)
            if not marshaller_context.top:
                return items
            return [marshal(i, marshaller, func=func, args=args, kwargs=kwargs, **marshaller_kwargs) for i in items]
        wrapper.marshalled_with = marshaller
        return wrapper
    return decorator


def marshal_dict_with(**mapping):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            data = func(*args, **kwargs)
            out = {}
            for k, v in data.iteritems():
                if k in mapping:
                    out[k] = marshal(v, mapping[k], func=func, args=args, kwargs=kwargs)
                else:
                    out[k] = v
            return out
        wrapper.marshalled_with = mapping
        return wrapper
    return decorator
