# -*- coding: utf-8 -*-
from __future__ import print_function

import types

__doc__ = """
    This module contains decorator generators.
    Essentially this will be a medley of delicious functions
    to generate relatively useful, reusable, generic decorators for code.
"""


def function_registrator(target):
    """ function_registrator generates a simple decorator that will
        take a function with any set of arguments and register that
        function within a target list.
    """

    def decorator(func):
        """ This is a "flexible" decorator function that pushes to
            target thanks to scope magic.
        """

        if func not in target:
            target.append(func)

        return func

    return decorator


def function_marker(attr, value):
    """ function_marker generates a simple decorator that will
        take a function with any set of arguments and set a given
        attribute on that function with setattr().
    """

    def decorator(func):
        """ This is a "flexible" decorator function that sets the
            attribute on the target function.
        """

        setattr(func, attr, value)

        return func

    return decorator


def function_kw_reg(target, req_args):
    """ function_kw_reg generates a more complex decorator that
        must be used with the argument names given in req_args.
        useful for attribute-based assertion.

        NOTE: target should be a dict-typed class

        :Example:

            trait = function_kw_reg(target, ['val1', 'val2', 'val3'])

            @trait(val1 = "attr1", val2 = "attr2", val3 = "attr3")
            def do_thing(...):
                pass
    """

    def decorator_outer(**kw):

        for req in req_args:
            if req not in kw.keys():
                raise KeyError("Missing required attribute: %s" % (req))

        def decorator_inner(func):

            if func not in target:
                target.update({func: kw})

            return func

        return decorator_inner

    return decorator_outer


def function_intercept_scope(*fs, **kwa):
    """ function_intercept_scope allows the injection of variables
        into a decorated function from a specified function or a
        list of functions. Variables injected are based on the return
        value of the function(s) provided.

        Provided functions should return a dictionary of kv pairs, with
        the key being a string and the value being any object to be injected.

        If intercept_args is True, *args and **kw going to the function
        be sent to the intercepting functions first.

        :Example:

            def intercept_argparser_inst(*args, **kw):

                if 'args' in kw:
                    argparser = kw['args']
                else:
                    argparser = CommandModuleLoader(state="default") \
                                .get_argument_parser()

                return {
                    "argparser": argparser
                }

            command_func = function_intercept_scope(
                intercept_argparser_inst,
                intercept_args=True)

            class ExampleModule(module.CommandModule):
                # ... all command module init, etc ...

                @command_func
                def command_do(self, *args, **kw):
                    global argparser
                    # 'argparser' will be injected here as a global
                    # do stuff ...

        .. warning:: This decorator is currently EXPERIMENTAL!
    """

    intercept_args = kwa.get('intercept_args', False)

    _funcs = []
    for fun in fs:
        if type(fun) in [types.FunctionType, types.LambdaType]:
            _funcs.append(fun)

    def decorator_outer(func):

        def decorator_inner(*args, **kw):

            try:
                fg = func.func_globals
            except (AttributeError):  # func_globals -> __globals__ on py3x
                fg = func.__globals__
            restore = {}
            _sentinel = object()

            inject = {}
            for fun in _funcs:
                try:
                    if intercept_args:
                        fi = fun(*args, **kw)
                    else:
                        fi = fun()

                    if not isinstance(fi, dict):
                        continue

                    inject.update(fi)
                except Exception as e:
                    print("Encountered an Exception while running interceptor:", fun)
                    print("Exception:", e)
                    continue

            for var in inject.keys():
                restore[var] = fg.get(var, _sentinel)
                fg[var] = inject[var]

            try:
                res = func(*args, **kw)
            finally:
                for var in inject.keys():
                    if restore[var] is _sentinel:
                        del fg[var]
                    else:
                        fg[var] = restore[var]

            return res

        return decorator_inner

    return decorator_outer
