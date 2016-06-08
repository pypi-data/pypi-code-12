#
# This file is part of RESORT.
#
# RESORT is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# RESORT is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with RESORT.  If not, see <http://www.gnu.org/licenses/>.
#

import collections

"""
Component execution classes.
"""

class Context:

	"""
	Execution context.

	:param str base_dir:
	   Base directory.
	:param str prof_dir:
	   Profile working directory.
	:param str prof_name:
	   Profile name.
	"""
	
	def __init__(self, base_dir, prof_dir, prof_name):
	
		self.__base_dir = base_dir
		self.__prof_dir = prof_dir
		self.__prof_name = prof_name
		
	def resolve(self, value):
	
		"""
		Resolve contextual value.

		:param value:
		   Contextual value.
		:return:
		   If value is a function with a single parameter, which is a read-only
		   dictionary, the return value of the function called with context
		   properties as its parameter. If not, the value itself.
		"""
		
		if isinstance(value, collections.Callable):
			return value({
				"base_dir": self.__base_dir,
				"profile_dir": self.__prof_dir,
				"profile_name": self.__prof_name
			})
		return value
		
class Operation:

	"""
	Component operation.
	
	:param str name:
	   Target component name.
	:param Component comp:
	   Target component. May be ``None``.
	"""
	
	def __init__(self, name, comp):
	
		self.__name = name
		self.__comp = comp
		if self.__comp is None:
			self.__execute = self.__execute_empty
		else:
			self.__execute = self.__execute_default
			
	def __eq__(self, other):
	
		return type(self) == type(other) and self.__name == other.__name
		
	def __ne__(self, other):
	
		return type(self) != type(other) or self.__name != other.__name
		
	def __repr__(self):
	
		return "{}.{}({}, {})".format(
			self.__module__,
			type(self).__name__,
			repr(self.__name),
			repr(self.__comp)
		)
		
	def __execute_empty(self, context):
	
		pass
		
	def __execute_default(self, context):
	
		self.execute_impl(self.__comp, context)
		
	def name(self):
	
		"""
		Component name.
		
		:rtype:
		   str
		"""
		
		return self.__name
		
	def execute(self, context):
	
		"""
		Execute operation.
		
		:param Context context:
		   Current execution context.
		"""
		
		self.__execute(context)
		
class Insert(Operation):

	"""
	Insert operation.
	
	:param str name:
	   Component name.
	:param Component comp:
	   Component to be inserted.
	"""
	
	def __init__(self, name, comp):
	
		super().__init__(name, comp)
		
	def execute_impl(self, comp, context):
	
		"""
		Execute insert operation.
		
		:param Component comp:
		   Target component.
		:param Context context:
		   Current context.
		"""
		
		comp.insert(context)
		
class Delete(Operation):

	"""
	Delete operation.
	
	:param str name:
	   Component name.
	:param Component comp:
	   Component to be deleted.
	"""
	
	def __init__(self, name, comp):
	
		super().__init__(name, comp)
		
	def execute_impl(self, comp, context):
	
		"""
		Execute delete operation.
		
		:param Component comp:
		   Target component.
		:param Context context:
		   Current context.
		"""
		
		comp.delete(context)

