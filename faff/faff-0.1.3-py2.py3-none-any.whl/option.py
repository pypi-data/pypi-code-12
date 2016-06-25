#!/usr/bin/env python


class Option(object):
    '''
    Option decorator class.
    '''

    class _Option(object):
        '''
        Internal option class.
        '''
        def __init__(self, arg_args, arg_kwargs, **kwargs):
            self._arg_args = arg_args
            self._arg_kwargs = arg_kwargs
            # TODO: Check name/function arguments.
            self._name = kwargs.get('name', None)
            self._func = kwargs.get('func', None)

        def __call__(self, opts):
            self._func(opts)

        def get_name(self):
            '''
            Get option name used as destination key.
            '''
            return self._name

        def add_argument(self, parser):
            '''
            Add self as option to parser with name as destination key.
            '''
            self._arg_kwargs.setdefault('dest', self._name)
            parser.add_argument(*self._arg_args, **self._arg_kwargs)

    def __init__(self, *args, **kwargs):
        # Store decorator positional and keyword arguments internally.
        self._arg_args = args
        self._arg_kwargs = kwargs
        self._kwargs = {}

    def __call__(self, func):
        # Use decorated function and name to create rule.
        self._kwargs.setdefault('name', func.__name__)
        self._kwargs.setdefault('func', func)
        return self._Option(self._arg_args, self._arg_kwargs, **self._kwargs)

    @staticmethod
    def is_option(obj):
        '''
        Test if object is an option (instance of Option._Option).
        '''
        if isinstance(obj, Option._Option):
            return True
        return False
