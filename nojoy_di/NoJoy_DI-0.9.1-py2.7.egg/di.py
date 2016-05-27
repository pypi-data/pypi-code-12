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
#    along with NoJoy_DI.  If not, see <http://www.gnu.org/licenses/>.
#
# Filename:  by: andrek
# Timesamp: 5/1/16 :: 10:25 PM


import functools
import sys

from NoJoy_DI.service import Service
from NoJoy_DI.utils import *
from NoJoy_DI.patterns import *
from NoJoy_DI.exceptions import *
#version hack
if sys.version_info >= (3,3):
	from inspect import signature, Parameter
	signature_empty = Parameter.empty
else:
	from funcsigs import signature
	from funcsigs import _empty as signature_empty


class DI(object):
	"""
	Joyiders Norse Dependency Injection Classifcation container!
	"""

	my_patterns = []
	my_patterns_cls = []

	def __init__(self):
		super(DI, self).__init__()
		self.services = {}
		self.variables = {}
		self.my_service_name = object_name_standard(self.__class__)
		#print(object_name_standard(self.__class__))
		self.create_patterns(SingletonPattern, DefaultPattern, BorgPattern)


	def create_patterns(self, *trees):
		"""
		Load the design patterns from patterns.py

		:param trees: Args of patterns to load
		:return: Nothing
		"""
		these_patterns = []
		these_patterns_cls = []

		for tree in trees:
			if isinstance(tree, BasePattern):
				these_patterns.append(tree)
				these_patterns_cls.append(tree.__class__)
			else:
				these_patterns.append(tree())
				these_patterns_cls.append(tree)
		self.my_patterns = tuple(these_patterns)
		self.my_patterns_cls = dict([(obj, inst) for inst, obj in enumerate(tuple(these_patterns_cls))])

	def set(self, name):
		svc = Service(name)
		self.services[svc.name] = svc
		return svc


	def attempt(self, name,shared=False):
		"""
		Add a NON existing service to the DI container

		:param name: The service to be added
		:param shared: Shared service or not Default False(DefaultPattern)
		:return: Service if success, false if service already exists in Container
		"""
		if object_name_standard(name) not in self.services:
			s = Service(name)
			if isinstance(shared, bool) and shared:
				s.set_pattern(SingletonPattern)
			self.services[s.name] = s
			return s
		return False

	def has_service(self, service):
		"""
		Checks whether the DI contains the Service

		:param service: The service to check if exists
		:return: True if the service exists else False
		"""
		name = object_name_standard(service)
		if name in self.services or name == self.my_service_name:
			return True
		else:
			return False


	def has_variable(self, variabel):
		"""
		Checks whether the DI contains the variable

		:param variabel: The variable to check if exists
		:return: True if the variable exists otherwise False
		"""
		if object_name_standard(variabel) in self.variables:
			return True
		else:
			return False


	def get(self, service):
		"""
		Will instantiate and return the service as an instance

		>>> di.get(AClass)
		<AClass object at 0x10d174c90>
		>>> isinstance(di.get(AClass), AClass)
		True

		:param service: Service to instantiate
		:return: The Instantiated class
		"""
		name = object_name_standard(service)
		if self.has_service(name):
			return self._get_data(service)
		raise Exception("Unknown Service or Service not available: " + name)

	def get_raw(self, service):
		"""
		Will return the `Raw` Service of the Class

		:param service: Service to get Raw data from
		:return: Class: Service for your service
		"""
		name = object_name_standard(service)
		if name not in self.services:
			raise Exception("Raise Error unknown service: " + name)
		return self.services[name]


	def add_variable(self, name, value):
		"""
		Add a variable to the DI Container

		>>>di.add_variable("A_variable", "The variable value")

		:param name: Name of the Variabel
		:param value: Value Of the Variable
		:return: Nothing
		"""
		self.variables[name] = value


	def get_variable(self, name):
		"""
		Will return the variable [name] from the DI Container

		>>> di.get_variable("A_variable")
		'The variable value'

		:param name: Name of the Variable
		:return: Value of variable [name]
		"""
		if name in self.variables:
			return self.variables[name]
		else:
			raise Exception("Unknown variable name: " + name)


	def _get_data(self, myservice, req_tokens=None):
		name = object_name_standard(myservice)

		if name == self.my_service_name:
			return self

		if not self.has_service(myservice):
			raise Exception("Raise Error unknown service: " + name)

		service_definition = self.services.get(name)
		my_tree = service_definition._mypattern

		if not my_tree in self.my_patterns_cls:
			raise Exception("Unknown pattern state")

		tree_idx = self.my_patterns_cls[my_tree]

		if not req_tokens:
			req_tokens = []
		else:
			req_tree = req_tokens[-1]._mypattern
			if req_tree and tree_idx > self.my_patterns_cls[req_tree]:
				raise PatternizerException(service_definition, req_tokens)

		def transformer(v):
			if isinstance(v, LazyMarker):
				return v.transformer(lambda name: self._get_data(name, req_tokens + [service_definition]), self.get_variable)
			else:
				return v

		def service_maker():
			return self._make(service_definition, transformer)

		return self.my_patterns[tree_idx].get(service_maker, name)

	def _update_input_from_signature(self, function, types_kwargs):
		try:
			sig = signature(function)
		except ValueError:
			return

		for name, parameter in tuple(sig.parameters.items()):
			if name == "self":
				continue
			if parameter.annotation is signature_empty:
				continue
			object_name = object_name_standard(parameter.annotation)

			if object_name in self.services:
				types_kwargs.setdefault(name, LazyMarker(service=object_name))


	def _make(self, svc_def, transformer):
		svc_def._locked = True

		def transform_input(types_kwargs):
			return dict([(key, transformer(value)) for key, value in types_kwargs.items()])

		if svc_def._factory:
			cls = transformer(svc_def._factory)
		else:
			cls = svc_def._get_classification()

		types_kwargs = dict(svc_def._input)
		self._update_input_from_signature(cls.__init__, types_kwargs)

		types_kwargs = transform_input((types_kwargs))

		for config in svc_def._arguments_injectors:
			transformer(config)(types_kwargs)

		myinstance = cls(**types_kwargs)

		for config in svc_def._injectors:
			transformer(config)(myinstance)

		for key, value in transform_input(svc_def._sets).items():
			setattr(myinstance, key, value)

		for active_signature, caller_function, caller_input in svc_def._callers:
			callable = getattr(myinstance, caller_function)
			types_kwargs = dict(caller_input)
			if active_signature:
				self._update_input_from_signature(callable, types_kwargs)
			callable(**transform_input(types_kwargs))

		return myinstance
