#!/usr/bin/python
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
#
# Filename: trees by: andrek
# Timesamp: 2016-05-02 :: 11:47
"""Patterns for NoJoy_DI
.. moduleauthor:: André Karlsson <andre@sess.se>
"""


class BasePattern(object):

	def get(self, c, name):
		raise NotImplementedError()


class DefaultPattern(BasePattern):

	def get(self, c, name):
		return c()


class SingletonPattern(BasePattern):
	"""
	Lazy instantioation of the Singlton Pattern
	"""
	def __init__(self):
		super(SingletonPattern, self).__init__()
		self.instances = {}

	def get(self, c, name):
		if name not in self.instances:
			self.instances[name] = c()
		return self.instances[name]


class BorgPattern(BasePattern): #TODO Not working with set (parameters and service)
	"""
	Execution of the Borg (Monostate pattern)

	"""
	__instances = {}

	def __init__(self):
		super(BorgPattern, self).__init__()

	def get(self, c, name):
		"""
		Get the instance based on the pattern to be used
		:param c:
		:param name:
		:return:
		"""
		if name not in self.__instances:
			self.__instances[name] = c()
			return self.__instances[name]
		theborg = c()
		theborg.__dict__ = self.__instances[name].__dict__
		return theborg
