import traceback
from functools import wraps
from types import MethodType, GeneratorType

from prosodypy.decorators import lua_object_method

class ModuleWrapper(object):
    def __init__(self, module):
        self.module = module

    def __getattr__(self, key):
        if key == 'module':
            return super(ModuleWrapper, self).__getattr__(key)
        value = getattr(self.module, key)
        if callable(value):
            return lambda *args: value(self.module, *args)
        return value

    def __setattr__(self, key, value):
        if key == 'module':
            return super(ModuleWrapper, self).__setattr__(key, value)
        return setattr(self.module, key, value)

    def __hasattr__(self, key):
        return hasattr(self.module, key)

def loggable_iterator_wrapper(self, iterator):
    try:
        for value in iterator:
            yield value
    except Exception:
        self.module.log(
            "error", "Python exception: %s", traceback.format_exc()
        )
        raise

def loggable(self, func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception as exc:
            self.module.log(
                "error", "Python exception: %s", traceback.format_exc()
            )
            raise
        if isinstance(result, GeneratorType):
            return loggable_iterator_wrapper(self, result)
        return result
    return inner

class ProsodyBasePlugin(object):
    """
    Base Prosody plugin class to be derived by all different plugins.

    Mimics the module:* callbacks from prosody as object methods.

    Has self.env and self.module attributes to access prosody APIs.
    """

    def __init__(self, env, lua):
        self.env = env
        self._module = env.module
        self.module = ModuleWrapper(self._module)
        self.prosody = env.prosody
        self.lua = lua
        for module_method in (
            'load',
            'save',
            'restore',
            'unload',
            'add_host',
        ):
            if hasattr(self, module_method):
                setattr(
                    self.module, module_method,
                    lua_object_method(getattr(self, module_method), lua)
                )

        for key in dir(self):
            method = getattr(self, key)
            if not key.startswith('__') and isinstance(method, MethodType):
                setattr(self, key, loggable(self, method))

    def __call__(self, *args):
        pass

