from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import functools
import inspect
import sys
from types import MethodType


from immunio.timer import DummyTimer


# Global store of all current monkeypatches. Used by `unwrap_all()` to remove
# all patching.
_PATCHES = {}


def unwrap_all():
    """
    Unwrap all monkeypatching done with the `@monkeypatch()` decorator.
    """
    global _PATCHES

    # Loop through ever patch and unwrap it. Converted to a list since doing
    # the unpatching will mutate the `_PATCHES` dict.
    for _, wrapped in list(_PATCHES.items()):
        wrapped.immunio_unwrap()


def monkeypatch(target_or_base, target=None, timer=None, report_name=None):
    """
    Monkeypatch the specified target with the decorated function.

    If only one argument is provided, it must be a string referencing the
    function to monkey patch.

    If two arguments are specified, the first must be a module or class,
    and the second must be a string referencing the attribute to be
    monkey patched.

    Example usage:

    class SomeClass(object):
        def some_method(self, a, b, c):
            pass

    To wrap `some_method()` above, you use monkeypatch like this when
    defining a wrapped function:

    @monkeypatch(SomeClass, "some_method")
    def _my_version(orig, self, a, b, c):
        # Here, self, a, b, c are the exact arguments that would have been
        # passed to the original `some_method()`. `orig` is a reference to
        # the original unwrapped version of the mthod. This allows you to
        # call the original version of the method.

        return orig(self, a, b, c)

    """
    global _PATCHES

    # If a timer is provided, and name must be provided
    if timer and not report_name:
        raise ValueError("If a `timer` is specified, `report_name` must be too")

    # If no timer object is provided, use a dummy
    if timer is None:
        timer = DummyTimer()

    # Validate we have the correct number and type of arguments
    if target is None and not isinstance(target_or_base, basestring):
        raise ValueError("Invalid arguments to monkeypatch()")
    if target is not None and not isinstance(target, basestring):
        raise ValueError("Invalid arguments to monkeypatch()")

    # If the first argument is a string, resolve the base and target from there.
    if isinstance(target_or_base, basestring):
        parts = target_or_base.split(".")
        base = sys.modules[parts[0]]

        for part in parts[1:-1]:
            base = getattr(base, part)
        target = parts[-1]
    else:
        # If the first argument is not a string, it IS the base.
        base = target_or_base

    is_instance = (not inspect.ismodule(base) and not inspect.isclass(base))
    def wrapper(wrapped):
        """
        This `wrapper` function is called with the new function as it's single
        argument.
        """
        # Get a reference to the original version of the function we're wrapping
        original = getattr(base, target)

        # Determine what type of function/method we're wrapping
        is_bare_function = inspect.isfunction(original)
        is_bound = inspect.ismethod(original) and original.__self__ is base
        is_instancemethod = is_bound and is_instance
        is_classmethod = is_bound and not is_instance
        is_staticmethod = is_bare_function and inspect.isclass(base)

        # For bound methods, we need to access the underlying bare function.
        # This allows `orig()` to be called with our supplied first argument
        # in the same way as wrapped instance methods.
        bound_original = None
        if is_bound:
            bound_original = original
            original = original.__func__

        # If we're already wrapped the original before, don't double-wrap it,
        # wrap the original version instead.
        if hasattr(original, "_immunio_original"):
            original = original._immunio_original

        # Define the new replacement function. The replacement just calls
        # the decorated function with the additional `orig` argument. The
        # `orig` argument is a timing wrapper around the real original.
        #
        # If the replacement function `wrapped` is a generator, we use
        # generator versions of the replacement functions so that the timer
        # works correctly.
        if inspect.isgeneratorfunction(wrapped):
            # GENERATOR VERSIONS
            def timed_original(*args, **kwargs):
                original_gen = original(*args, **kwargs)
                while True:
                    # Here we exclude just the time spent in the original
                    with timer(exclude=True):
                        x = original_gen.next()
                    yield x

            @functools.wraps(original)
            def new_wrapped(*args, **kwargs):
                # Here we time the whole duration
                with timer(report_name):
                    for x in wrapped(timed_original, *args, **kwargs):
                        yield x
        else:
            # RETURNING VERSIONS
            def timed_original(*args, **kwargs):
                # Wrap in a timer to exclude time spent in the original
                with timer(exclude=True):
                    return original(*args, **kwargs)

            @functools.wraps(original)
            def new_wrapped(*args, **kwargs):
                with timer(report_name):
                    return wrapped(timed_original, *args, **kwargs)

        # Add the `_immunio_original` function attribute so we keep a reference
        # to the unwrapped version of the function.
        setattr(new_wrapped, "_immunio_original", original)

        # Copy any method level properties to the wrapper. Django after 1.8 uses
        # the values `queryset_only` and `alters_data` for the creation of
        # managers.
        if hasattr(original, "__dict__"):
            for (key, value) in original.__dict__.items():
                setattr(new_wrapped, key, value)

        def unwrap():
            """
            Remove the Immunio wrapping from this function.
            """
            orig = getattr(base, target)._immunio_original
            # Remove the reference from the global patches dict
            del _PATCHES[orig]
            # Add back the required decorators
            if is_bound:
                orig = bound_original
            elif is_staticmethod:
                orig = staticmethod(orig)
            setattr(base, target, orig)

        # Add an `immunio_unwrap()` attribute to the wrapped function to allow
        # our wrapping to be "undone".
        setattr(new_wrapped, "immunio_unwrap", unwrap)
        # Save a reference to this wrapped function so we can unwrap it later.
        _PATCHES[original] = new_wrapped

        # Wrapped classmethods need to be re-marked as a classmethod so the
        # class is bound as the first argument
        if is_classmethod:
            new_wrapped = classmethod(new_wrapped)

        # A bare method (or a staticmethod) being added to a class need to be
        # re-marked as a staticmethod to prevent them from being bound to the
        # class like an instance method.
        if is_staticmethod:
            new_wrapped = staticmethod(new_wrapped)

        # If we're applying this method to just one instance then it has to
        # be bound to that instance.
        if is_instancemethod:
            new_wrapped = MethodType(new_wrapped, base)

        # Overwrite the original version with our wrapped version
        setattr(base, target, new_wrapped)

        return wrapped
    return wrapper
