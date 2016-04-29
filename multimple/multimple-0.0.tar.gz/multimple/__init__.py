from functools import wraps


__version__ = "0.0"


class Multimple(object):
    _IMPL_ATTR_NAME = "_multimple_current"

    def __init__(self, func, default):
        super(Multimple, self).__init__()

        self._impls = {
            default: func
        }
        self._default = default
        self._name = func.__name__

    def __get__(self, owner, klass=None):
        current_impl = getattr(owner, self._IMPL_ATTR_NAME, None)

        impl = None
        if not current_impl:
            impl = self._impls.get(self._default)
        else:
            impl = self._impls.get(current_impl)

        if not impl:
            raise NotImplementedError(
                "'{}' is not implemented for '{}'".format(
                    self._name,
                    current_impl
                )
            )

        return impl.__get__(owner, klass)

    @classmethod
    def decorator(cls, arg):
        if isinstance(arg, type):
            return cls.class_decorator(arg)
        else:
            return cls.func_decorator(arg)

    @classmethod
    def func_decorator(cls, impl_name):
        def wrapper(func):
            mio = cls(func, default=impl_name)

            return mio

        return wrapper

    @classmethod
    def class_decorator(cls, klass):
        @classmethod
        def get_implementation(target, impl_name):
            @wraps(target.__init__)
            def init(*args, **kwargs):
                obj = target(*args, **kwargs)
                setattr(obj, cls._IMPL_ATTR_NAME, impl_name)

                return obj

            return init

        setattr(klass, 'multimple', get_implementation)

        return klass

    def multimple(self, impl_name):
        def wrapper(func):
            self._impls[impl_name] = func

            return self

        return wrapper


multimple = Multimple.decorator  # pylint: disable=invalid-name
