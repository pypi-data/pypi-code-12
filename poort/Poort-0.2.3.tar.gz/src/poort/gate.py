# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from .request import Request
from threading import local

_local = local()


class Gate(object):
    """Gate is a local storage container (DI of some sorts).

    You should extend this class and provide extra methods and properties
    that you use throughout your application.

    .. code-block:: python

        import poort

        gate = poort.Gate()

        def application(environ, start_response):
            with gate(environ):
                request = gate.request

                if request.path == '/':
                    response = poort.Response('Hallo world!')
                else:
                    response = poort.Response('Not found.', status_code=404)

                return response(request, start_response)

    How to extend `poort.Gate`

    .. code-block:: python

        import poort


        class Gate(poort.Gate):
            def setup(self, environ, *args, **kwargs):
                super(Gate, self).setup(environ, *args, **kwargs)

                dbname = 'test-app'
                self.attach('database', Database(dbname))

            @property
            def database(self):
                ''':rtype: Database'''
                return self.retrieve('database')


        gate = Gate()


        def application(environ, start_response):
            with gate(environ):
                request = gate.request
                database = gate.database

                if request.path == '/':
                    response = poort.Response('Hallo world!')
                else:
                    response = poort.Response('Not found.', status_code=404)

                return response(request, start_response)

    """

    def __init__(self):
        self.local = local()

    def setup(self, environ, *args, **kwargs):
        """Override this method when extending `poort.Gate`.

        :param environ: Environment dict of the WSGI request.

        :type environ: dict

        """
        if hasattr(self.local, 'gate_registered_names'):
            raise RuntimeError('Gate already started.')

        self.local.gate_registered_names = set()
        self.attach('request', Request(environ))

    def teardown(self):
        if not hasattr(self.local, 'gate_registered_names'):
            raise RuntimeError('Gate not started.')

        for name in self.local.gate_registered_names:
            delattr(self.local, name)
        delattr(self.local, 'gate_registered_names')

    def __call__(self, *args, **kwargs):
        self.setup(*args, **kwargs)
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.teardown()

    def attach(self, name, value):
        self.local.gate_registered_names.add(name)
        setattr(self.local, name, value)

    def contains(self, name):
        return name in self.local.gate_registered_names

    def retrieve(self, name):
        if not self.contains(name):
            raise ValueError('Property `{:s}` is not attached.'.format(
                name))
        return getattr(self.local, name)

    def release(self, name):
        self.local.gate_registered_names.remove(name)
        delattr(self.local, name)

    @property
    def request(self):
        """

        :rtype: poort.Request
        """
        return self.retrieve('request')
