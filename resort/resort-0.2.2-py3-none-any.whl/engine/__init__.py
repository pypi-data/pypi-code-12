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

"""
Package containing engine classes.
"""

import configparser
import os

class ProfileManager:

	"""
	Manager for profiles located in a directory.
	
	:param str base_dir:
	   Directory path of this manager. Must be absolute.
	:param str work_dir:
	   Working directory. From base_dir if it is relative.
	:param dict profiles:
	   Dictionary containing profile type and instance entries.
	"""
	
	def __init__(self, base_dir, work_dir, profiles):
	
		if not os.path.isabs(base_dir):
			msg = "{} is not absolute".format(base_dir)
			raise Exception(msg)
		self.__base_dir = base_dir
		
		if os.path.isabs(work_dir):
			self.__work_dir = work_dir
		else:
			self.__work_dir = os.path.join(self.__base_dir, work_dir)
			
		self.__profiles = profiles or {}
		
	def __profile_stub(self, prof_name, prof_type, prof_dir):
	
		try:
			prof = self.__profiles[prof_type]
			return ProfileStub(self.__base_dir, prof_name, prof, prof_dir)
		except KeyError:
			msg = "Profile of type '{}' does not exist"
			raise Exception(msg.format(prof_type))
			
	def __profile_dir(self, prof_name):
	
		return os.path.join(self.__work_dir, prof_name)
		
	def __profile_ini_path(self, prof_dir):
	
		return os.path.join(prof_dir, "profile.ini")
		
	def load(self, prof_name):
	
		"""
		Load the profile with the given name.
		
		:param str prof_name:
		   Profile name.
		:rtype:
		   ProfileStub
		:return:
		   An stub to loaded profile.
		"""
		
		prof_dir = self.__profile_dir(prof_name)
		prof_ini_path = self.__profile_ini_path(prof_dir)
		if not os.path.exists(prof_ini_path):
			msg = "Profile '{}' does not exist"
			raise Exception(msg.format(prof_name))
			
		# Load profile
		prof_ini_file = open(prof_ini_path, "r")
		prof_ini = configparser.ConfigParser()
		prof_ini.read_file(prof_ini_file)
		prof_ini_file.close()
		
		# Prepare profile
		prof_type = prof_ini["profile"]["type"]
		prof_stub = self.__profile_stub(prof_name, prof_type, prof_dir)
		prof_stub.prepare(prof_ini["properties"])
		
		return prof_stub
		
	def store(self, prof_name, prof_type):
	
		"""
		Store a profile with the given name and type.
		
		:param str prof_name:
		   Profile name.
		:param str prof_type:
		   Profile type.
		"""
		
		prof_dir = self.__profile_dir(prof_name)
		prof_stub = self.__profile_stub(prof_name, prof_type, prof_dir)
		if not os.path.exists(prof_dir):
			os.makedirs(prof_dir)
		prof_ini_path = self.__profile_ini_path(prof_dir)
		
		# Load previous properties
		if os.path.exists(prof_ini_path):
			prof_ini_file = open(prof_ini_path, "r")
			prof_ini = configparser.ConfigParser()
			prof_ini.read_file(prof_ini_file)
			prof_ini_file.close()
			prev_props = prof_ini["properties"]
		else:
			prev_props = {}
			
		# Prepare and store profile
		prof_ini = configparser.ConfigParser()
		prof_ini["profile"] = {}
		prof_ini["profile"]["type"] = prof_type
		prof_ini["properties"] = prof_stub.prepare(prev_props)
		prof_ini_file = open(prof_ini_path, "w")
		prof_ini.write(prof_ini_file)
		prof_ini_file.close()
		
class ProfileStub:

	"""
	Stub of a :class:`Profile` with a :class:`ComponentStubRegistry`.
	
	:param str prof_name:
	   Profile name.
	:param Profile prof:
	   Profile instance.
	:param str prof_dir:
	   Profile working directory.
	"""
	
	def __init__(self, base_dir, prof_name, prof, prof_dir):
	
		self.__base_dir = base_dir
		self.__prof_name = prof_name
		self.__prof = prof
		self.__prof_dir = prof_dir
		self.__comp_stub_reg = ComponentStubRegistry(self.__prof)
		
	def __component_list(self, comp_stub, target_list):
	
		if comp_stub not in target_list:
			target_list.append(comp_stub)
		for dep_stub in comp_stub.dependencies():
			self.__component_list(dep_stub, target_list)
			
	def context(self):
	
		"""
		Create an exectution context.
		
		:rtype:
		   execution.Context
		:return:
		   The created execution context.
		"""
		
		return execution.Context(self.__base_dir, self.__prof_dir,
				self.__prof_name)
		
	def prepare(self, props):
	
		"""
		Prepare stubbed profile and return its properties.
		
		:param dict props:
		   Dictionary with previous properties.
		:rtype:
		   dict
		:return:
		   Properties dictionary.
		"""
		
		return self.__prof.prepare(props)
		
	def component_list(self):
	
		"""
		List of :class:`ComponentStub` instances for this profile.
		
		:rtype:
		   list
		"""
		
		comp_list = []
		self.__component_list(self.component(None), comp_list)
		return sorted(comp_list)
		
	def component(self, comp_name):
	
		"""
		Component with the specified name.
		
		:param str comp_name:
		   Specified component name.
		:rtype:
		   ComponentStub
		:return:
		   The component stub with the specified name.
		"""
		
		return self.__comp_stub_reg.get(comp_name)
		
class ComponentStub:

	"""
	Stub of a :class:`Component`.
	
	:param ComponentStubRegistry comp_stub_reg:
	   Component stub registry.
	:param str comp_name:
	   Component name.
	:param Profile prof:
	   Owner profile.
	"""
	
	def __init__(self, comp_stub_reg, comp_name, prof):
	
		self.__comp_stub_reg = comp_stub_reg
		self.__comp_name = comp_name
		self.__comp_inst = None
		self.__comp = self.__comp_init
		self.__prof = prof
		self.__type_name = self.__type_name_init
		self.__available = self.__available_init
		
	def __eq__(self, other):
	
		return self.name() == other.name()
		
	def __ne__(self, other):
	
		return self.name() != other.name()
		
	def __lt__(self, other):
	
		if self.name() is None or other.name() is None:
			return None
		return self.name() < other.name()
		
	def __comp_init(self):
	
		self.__comp_inst = self.__prof.component(self.__comp_name)
		return self.__comp_inst
		
	def __comp_default(self):
	
		return self.__comp_inst
		
	def __type_name_init(self):
	
		comp = self.__comp()
		if comp is None:
			self.__type_name = self.__type_name_empty
		else:
			self.__type_name = self.__type_name_default
		return self.__type_name()
		
	def __type_name_empty(self):
	
		return None
		
	def __type_name_default(self):
	
		return "{}.{}".format(
			self.__comp_inst.__module__,
			self.__comp_inst.__class__.__name__
		)
		
	def __available_init(self, context):
	
		comp = self.__comp()
		if comp is None:
			self.__available = self.__available_empty
		else:
			self.__available = self.__available_default
		return self.__available(context)
		
	def __available_empty(self, context):
	
		return None
		
	def __available_default(self, context):
	
		return self.__comp_inst.available(context)
		
	def __dependents(self, comp_stub):
	
		for dep_stub in comp_stub.dependencies():
			if dep_stub == self:
				yield comp_stub
			else:
				yield from self.__dependents(dep_stub)
		yield from ()
		
	def name(self):
	
		"""
		Component name.
		
		:rtype:
		   str
		"""
		
		return self.__comp_name
		
	def type_name(self):
	
		"""
		Fully qualified name of component class or ``None``.
		
		:rtype:
		   str
		"""
		
		return self.__type_name()
		
	def dependencies(self):
	
		"""
		Yield :class:`ComponentStub` of dependencies of this component.
		"""
		
		try:
			for dep_name in self.__prof.dependencies(self.name()):
				yield self.__comp_stub_reg.get(dep_name)
		except TypeError:
			yield from ()
			
	def available(self, context):
	
		"""
		Return component availability.
		
		:rtype:
		   bool
		:return:
		   Component availability.
		"""
		
		return self.__available(context)
		
	def insert(self, context, plan):
	
		"""
		Include an insert operation to the given plan.
		
		:param execution.Context context:
		   Current execution context.
		:param list plan:
		   List of :class:`execution.Operation` instances.
		"""
		
		op = execution.Insert(self.__comp_name, self.__comp())
		if op not in plan and self.available(context) != True:
			for dep_stub in self.dependencies():
				dep_stub.insert(context, plan)
			plan.append(op)
			
	def delete(self, context, plan):
	
		"""
		Include a delete operation to the given plan.
		
		:param execution.Context context:
		   Current execution context.
		:param list plan:
		   List of :class:`execution.Operation` instances.
		"""
		
		op = execution.Delete(self.__comp_name, self.__comp())
		if op not in plan and self.available(context) != False:
			for dep_stub in self.__dependents(self.__comp_stub_reg.get(None)):
				dep_stub.delete(context, plan)
			plan.append(op)
			
class ComponentStubRegistry:

	"""
	Registry of :class:`ComponentStub`.
	
	:param Profile prof:
	   Involved profile.
	"""
	
	def __init__(self, prof):
	
		self.__prof = prof
		self.__cache = {}
		
	def get(self, comp_name):
	
		"""
		Get the specified component.
		
		:param str comp_name:
		   Specified component name.
		:rtype:
		   ComponentStub
		:return:
		   Specified component stub.
		"""
		
		try:
			return self.__cache[comp_name]
		except KeyError:
			comp_stub = ComponentStub(self, comp_name, self.__prof)
			self.__cache[comp_name] = comp_stub
			return comp_stub

