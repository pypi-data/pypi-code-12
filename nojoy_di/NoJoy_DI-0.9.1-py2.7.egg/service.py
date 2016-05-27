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
#    Foobar is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
#
# Filename:  by: andrek
# Timesamp: 5/1/16 :: 10:25 PM

import sys
from NoJoy_DI.utils import *
from NoJoy_DI.patterns import *
from functools import wraps
from importlib import import_module

#version hack
if sys.version_info >= (3,3):
	from inspect import signature, Parameter
	signature_empty = Parameter.empty
else:
	from funcsigs import signature
	from funcsigs import _empty as signature_empty


class Service(object):

	_mypattern = DefaultPattern
	_factory = None

	_classification = None
	_classification_getter = None
	_inject_signature = False

	_locked = False

	def __init__(self, mycallable, classification=None):
		super(Service, self).__init__()

		self._input = {}
		self._sets = {}
		self._callers = []
		self._injectors = []
		self._arguments_injectors = []

		self.name = object_name_standard(mycallable)

		if classification:
			self._classification = classification
		else:
			if callable(mycallable):
				self._classification = mycallable
			else:
				self._classification_getter = self._lazy_loader(mycallable)


	def _get_classification(self):
		if self._classification:
			return  self._classification
		if self._classification_getter:
			self._classification = self._classification_getter()
			return self._classification

		raise Exception()

	def _lazy_loader(self, class_hierarchy):
		module, cls = class_hierarchy.split('.', 1)
		@wraps(self._lazy_loader)
		def wrapper(*args, **kwargs):
			return getattr(import_module(module), cls)
		return  wrapper


	def _lazymarker(self, myclone=None, myservice=None, myfunction=None, myvariable=None):
		if myclone is not None:
			return myclone
		elif myservice or myvariable:
			return LazyMarker(service=myservice, function=myfunction, variable=myvariable)

	def _input_maker(self, kwargs):
		types = {}
		for key, value in kwargs.items():
			if key.endswith("__svc"):
				types[key[:-5]] = self._lazymarker(myservice=value)
			elif key.endswith("__param"):
				types[key[:-7]] = self._lazymarker(myvariable=value)
			else:
				types[key] = value
		return types

	@private
	def set_classification(self, value):
		"""
		Classify the service callable

		:param value:A callable method/function to be classified as service main callable
		:return:
		"""
		self._classification = value

	@private
	def set_factory(self, service=None, function=None, acallable=None):
		"""
		Create a factory callable to by assigning a Factory to a Service(Class)
		and set the private factroy accordingly

		>>> di.set(AFactory_Class)
		>>> di.set(A_Class).set_factory(service=AFactory_Class, function="return_class_method")

		:param service: The factory Service(class) it self
		:param function: Function/method to be called in the factory
		:param acallable: A already created LazyMarker
		:return:
		"""
		self._factory = self._lazymarker(myclone=acallable, myservice=service, myfunction=function)

	@private
	def input(self, **kwargs):
		"""
		Add constructor args for the service

		>>> di.set(AFactory_Class)
		>>> di.set(A_Class).set_factory(service=AFactory_Class, function="return_class_method").input(variable="abc")

		:param kwargs: Input arguments for the Service
		:return:
		"""
		self._input.update(self._input_maker(kwargs))

	@private
	def call(self, function, arg=False, **kwargs):
		"""
		Call method adds a method call with arguments on an existing Service

		:param function: The callable function/method
		:param arg: If True Argements will be detected using signature (used with set_signature) Default:False
		:param kwargs: Arguments for function/method
		:return:
		"""
		if isinstance(arg, bool):
			self._callers.append((arg, function, self._input_maker(kwargs)))
		else:
			raise Exception("Undefined Argument (arg)")


	@private
	def set(self, **kwargs):
		"""
		Using setattr to set the values to the instanstiated service

		>>> di.set(A_Class).set(variable="abc")

		:param kwargs: KeyWord arguments for the Service
		:return:
		"""
		self._sets.update(self._input_maker(kwargs))

	@private
	def injector(self, service=None, function=None, function_args=None,
	             acallable=None, callable_args=None):
		"""
		Injects a Service or callable into self Service

		>>> di.set(AnInjector_Class)
		>>> di.set(A_Class).injector(service=AnInjector, function="a_method", function_args="a_method_with_kwargs")

		:param service: Service to be injected to self
		:param function: method to to called for injected service
		:param function_args: method to to called WITH INPUTS for injected service
		:param acallable: callable to to called for injected service
		:param callable_args: callable to to called WITH INPUTS for injected service
		:return:
		"""
		if function or acallable:
			self._injectors.append(self._lazymarker(myclone=acallable, myservice=service, myfunction=function))
		if function_args or callable_args:
			self._arguments_injectors.append(self._lazymarker(myclone=callable_args,
			                                                  myservice=service,
			                                                  myfunction=function_args))

	@private
	def set_signature(self):
		self._inject_signature = True

	@private
	def set_pattern(self, pattern_cls):
		self._mypattern = pattern_cls

