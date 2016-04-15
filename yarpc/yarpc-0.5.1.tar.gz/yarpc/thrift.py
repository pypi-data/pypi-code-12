# Copyright (c) 2016 Uber Technologies, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

from types import ModuleType

import thriftrw

from yarpc.errors import OneWayNotSupportedError


def load(path, service=None):
    # get thriftrw module
    thriftrw_module = thriftrw.load(path)

    # start building a fresh module
    module = ModuleType(thriftrw_module.__name__)

    # attach services
    for service_cls in thriftrw_module.__services__:
        setattr(
            module,
            service_cls.service_spec.name,
            Service(service_cls, module, service),
        )

    # attach types
    for t in thriftrw_module.__types__:
        # __types__ contains primitive type defs in tuples,
        # we only want the types that have __name__
        if hasattr(t, '__name__'):
            setattr(module, t.__name__, t)

    # attach constants
    for k, v in thriftrw_module.__constants__.items():
        setattr(module, k, v)

    # TODO deal with includes...

    return module


class Service(object):

    def __init__(self, cls, module, service_name=None):

        self.service_spec = cls.service_spec

        # attach functions
        for func_spec in self.service_spec.functions:
            setattr(
                self,
                func_spec.name,
                Function(func_spec, self, module, service_name),
            )

    @property
    def name(self):
        """Name of the Thrift service this object represents."""
        return self.service_spec.name


class Function(object):

    def __init__(self, func_spec, service, module, service_name=None):
        self.spec = func_spec
        self.service = service

        self._func = func_spec.surface

        self.request = self._func.request
        self.request.service_name = service_name

        self.response_cls = self._func.response

        self._module = module

    @property
    def procedure(self):
        return '%s::%s' % (self.service.name, self._func.name)

    @property
    def oneway(self):
        return self.spec.oneway

    def __call__(self, *args, **kwargs):
        if self.oneway:
            raise OneWayNotSupportedError(
                'TChannel+Thrift does not currently support oneway '
                'procedures.'
            )
        call_args = self.request(*args, **kwargs)

        return call_args
