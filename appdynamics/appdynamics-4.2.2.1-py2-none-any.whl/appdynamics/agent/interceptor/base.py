# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Definition of base entry and exit point interceptors.

"""

import sys
from functools import wraps
from contextlib import contextmanager

from appdynamics.agent.core.correlation import make_header


class BaseInterceptor(object):
    def __init__(self, agent, cls):
        self.agent = agent
        self.cls = cls

    @property
    def bt(self):
        return self.agent.get_active_bt()

    def __setitem__(self, key, value):
        bt = self.bt
        if bt:
            bt._properties[key] = value

    def __getitem__(self, key):
        bt = self.bt
        if bt:
            return bt._properties.get(key)

    def __delitem__(self, key):
        bt = self.bt
        if bt:
            bt._properties.pop(key, None)

    def _fix_dunder_method_name(self, method, class_name):
        # If `method` starts with '__', then it will have been renamed by the lexer to '_SomeClass__some_method'
        # (unless the method name ends with '__').
        if method.startswith('__') and not method.endswith('__'):
            method = '_' + class_name + method
        return method

    def _attach(self, method, wrapper_func, patched_method_name):
        patched_method_name = patched_method_name or '_' + method

        # Deal with reserved identifiers.
        # https://docs.python.org/2/reference/lexical_analysis.html#reserved-classes-of-identifiers
        method = self._fix_dunder_method_name(method, self.cls.__name__)
        patched_method_name = self._fix_dunder_method_name(patched_method_name, self.__class__.__name__)

        # Wrap the orignal method if required.
        original_method = getattr(self.cls, method)

        # Do not intercept the same method more than once.
        if hasattr(original_method, '_appd_intercepted'):
            return

        if wrapper_func:
            @wraps(original_method)
            def wrapped_method(*args, **kwargs):
                return wrapper_func(original_method, *args, **kwargs)
            real_method = wrapped_method
        else:
            real_method = original_method

        # Replace `self.cls.method` with a call to the patched method.
        patched_method = getattr(self, patched_method_name)

        @wraps(original_method)
        def call_patched_method(*args, **kwargs):
            return patched_method(real_method, *args, **kwargs)
        call_patched_method._appd_intercepted = True

        setattr(self.cls, method, call_patched_method)

    def attach(self, method_or_methods, wrapper_func=None, patched_method_name=None):
        if not isinstance(method_or_methods, list):
            method_or_methods = [method_or_methods]
        for method in method_or_methods:
            self._attach(method, wrapper_func, patched_method_name)

    def log_exception(self, level=1):
        self.agent.logger.exception('Exception in {klass}.{function}.'.format(
            klass=self.__class__.__name__, function=sys._getframe(level).f_code.co_name))

    @contextmanager
    def log_exceptions(self):
        try:
            yield
        except:
            self.log_exception(level=3)

NO_WRAPPER = object()


class ExitCallInterceptor(BaseInterceptor):
    def attach(self, method_or_methods, wrapper_func=NO_WRAPPER, patched_method_name=None):
        if wrapper_func is NO_WRAPPER:
            wrapper_func = self.run
        super(ExitCallInterceptor, self).attach(method_or_methods, wrapper_func=wrapper_func,
                                                patched_method_name=patched_method_name)

    @property
    def exit_call(self):
        bt = self.bt
        if bt:
            return bt._active_exit_call

    def make_correlation_header(self):
        exit_call = self.exit_call
        header = make_header(self.agent, self.bt, exit_call)
        if exit_call:
            exit_call.backend.optional_properties['CorrelationHeader'] = header[1]
        return header

    def start_exit_call(self, bt, backend, operation=None, params=None):
        """Start an exit call.

        """
        with self.log_exceptions():
            caller = sys._getframe(3)
            return self.agent.start_exit_call(bt, caller, backend, operation=operation, params=params)

    def run(self, func, *args, **kwargs):
        """Run the function.  If it raises an exception, end the exit call and re-raise the exception.

        """
        with self.end_exit_call_and_reraise_on_exception():
            return func(*args, **kwargs)

    def end_exit_call(self, exc_info=None):
        """End the exit call.

        """
        with self.log_exceptions():
            exit_call = self.exit_call
            if exit_call:
                self.agent.end_exit_call(self.bt, exit_call, exc_info=exc_info)

    @contextmanager
    def end_exit_call_and_reraise_on_exception(self, ignored_exceptions=()):
        try:
            yield
        except ignored_exceptions:
            raise
        except:
            self.end_exit_call(exc_info=sys.exc_info())
            raise
