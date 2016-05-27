#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
# NoJoy_DI (c) 2016 by Andre Karlsson<andre.karlsson@protractus.se>
#
# This file is part of NoJoy_DI.
#
#    NoJoy_DI is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    NoJoy_DI is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
#
# Filename:  by: andrek
# Timesamp: 5/1/16 :: 10:23 PM

import functools
from inspect import isclass, isfunction, stack
from functools import wraps, partial, WRAPPER_ASSIGNMENTS

try:
    wraps(partial(wraps))(wraps)
except AttributeError:
    @wraps(wraps)
    def wraps(obj, attr_names=WRAPPER_ASSIGNMENTS, wraps=wraps):
        return wraps(obj, assigned=(name for name in attr_names if hasattr(obj, name)))

def object_name_standard(myobject):
    if isclass(myobject) or isfunction(myobject):
        #return "{0}.{1}".format(myobject.__module__, myobject.__name__)
        return "{0}".format(myobject.__name__)
    if isinstance(myobject, str):
        return myobject

    print("Error")


def private(myfunc):
	@wraps(myfunc)
	def wrapper(self, *args, **kwargs):
		if self._locked:
			print("Raise Service is already created")
		else:
			myfunc(self, *args, **kwargs)
		return self
	return wrapper


class LazyMarker(object):
    def __init__(self, service=None, function=None, variable=None):
        super(LazyMarker, self).__init__()
        self.service = service
        self.function = function
        self.variable = variable

    def transformer(self, getter, variable_getter):
        if self.service:
            s = getter(self.service)
            if self.function:
                return getattr(s, self.function)
            else:
                return s
        if self.variable:
            return variable_getter(self.variable)
        raise Exception()
