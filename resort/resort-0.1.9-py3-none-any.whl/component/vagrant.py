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

import io
import os
import subprocess

class VagrantObject:

	"""
	Vagrant object.
	"""
	
	def __init__(self):
	
		pass
		
	def read(self, cmd_args):
	
		"""
		Execute Vagrant read command.
		
		:param list cmd_args:
		   Command argument list.
		"""
		
		args = [
			"vagrant",
			"--machine-readable"
		]
		args.extend(cmd_args)
		proc = subprocess.Popen(args, stdout=subprocess.PIPE)
		for line in proc.stdout.readlines():
			if len(line) == 0:
				break
			yield line.decode("UTF-8").rsplit(",")
		proc.wait()
		
	def write(self, cmd_args):
	
		"""
		Execute Vagrant write command.
		
		:param list cmd_args:
		   Command argument list.
		"""
		
		args = [
			"vagrant"
		]
		args.extend(cmd_args)
		subprocess.call(args)
		
class BoxFile(VagrantObject):

	"""
	Vagrant box from file. Implements :class:`Component`.
	
	:param name_fn:
	   Box name function for the given context.
	:param str image_dir:
	   Box image directory.
	"""
	
	def __init__(self, name_fn, image_dir):
	
		self.__name_fn = name_fn
		self.__image_dir = image_dir
		self.__available = None
		
	def __box_list(self):
	
		result_entry = {}
		for line in self.read([
			"box",
			"list"
		]):
			key = line[2]
			value = line[3].strip()
			if key == "box-name":
				if len(result_entry) > 0:
					yield result_entry
					result_entry = {}
				result_entry["name"] = value
			elif key == "box-provider":
				result_entry["provider"] = value
			elif key == "box-version":
				result_entry["version"] = value
		if len(result_entry) > 0:
			yield result_entry
			
	def __path(self, context):
	
		for fname in os.listdir(os.path.join(context.profile_dir(),
				self.__image_dir)):
			if fname.endswith(".box"):
				return os.path.join(os.path.join(context.profile_dir(),
						self.__image_dir), fname)
		raise Exception("Box image not found at {}".format(self.__image_dir))
		
	def available(self, context):
	
		"""
		Box is available for the calling user.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		if self.__available is None:
			avail = False
			for box in self.__box_list():
				name = self.__name_fn(context)
				if box["name"] == name and box["version"] == "0":
					avail = True
					break
			self.__available = avail
		return self.__available
		
	def insert(self, context):
	
		"""
		Add Vagrant box to the calling user.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		self.write([
			"box",
			"add",
			"--name", self.__name_fn(context),
			self.__path(context)
		])
		
	def delete(self, context):
	
		"""
		Delete Vagrant box from the calling user.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		self.write([
			"box",
			"remove",
			self.__name_fn(context)
		])
		
class Instance(VagrantObject):

	"""
	Vagrant instance.
	
	:param str config_dir:
	   Profile relative configuration directory.
	:param name_fn:
	   Instance name function for the given context.
	"""
	
	def __init__(self, config_dir, name_fn):
	
		self.__config_dir = config_dir
		self.__name_fn = name_fn
		
	def read(self, context, cmd_args):
	
		"""
		Execute Vagrant read command on instance placed into configuration
		directory.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		:param list cmd_args:
		   Command argument list.
		"""
		
		try:
			current_dir = os.getcwd()
			os.chdir(os.path.join(context.profile_dir(), self.__config_dir))
			args = []
			args.extend(cmd_args)
			args.append(self.__name_fn(context))
			yield from super().read(args)
		finally:
			os.chdir(current_dir)
			
	def write(self, context, cmd_args):
	
		"""
		Execute Vagrant write command on instance placed into configuration
		directory.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		:param list cmd_args:
		   Command argument list.
		"""
		
		try:
			current_dir = os.getcwd()
			os.chdir(os.path.join(context.profile_dir(), self.__config_dir))
			args = []
			args.extend(cmd_args)
			args.append(self.__name_fn(context))
			super().write(args)
		finally:
			os.chdir(current_dir)
			
	def state(self, context):
	
		"""
		Get instance state.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		:rtype:
		   str
		:return:
		   Instance state name.
		"""
		
		state = None
		for line in self.read(context, [
			"status",
			self.__name_fn(context)
		]):
			if line[2] == "state":
				state = line[3].strip()
		return state
			
	def created(self):
	
		"""
		Instance created component.
		
		:rtype:
		   InstanceCreated
		"""
		
		return InstanceCreated(self)
		
	def running(self):
	
		"""
		Instance running component.
		
		:rtype:
		   InstanceRunning
		"""
		
		return InstanceRunning(self)
		
class InstanceCreated:

	"""
	Vagrant instance created. Implements :class:`Component`.
	
	:param Instance inst:
	   Managed instance.
	"""
	
	def __init__(self, inst):
	
		self.__inst = inst
		self.__available = None
		
	def available(self, context):
	
		"""
		Check availability.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		:rtype:
		   bool
		:return:
		   Availability value.
		"""
		if self.__available is None:
			state = self.__inst.state(context)
			self.__available = state is not None and state != "not_created"
		return self.__available
		
	def insert(self, context):
	
		"""
		Create instance.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		self.__inst.write(context, [
			"up"
		])
		
	def delete(self, context):
	
		"""
		Delete instance.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		self.__inst.write(context, [
			"destroy",
			"-f"
		])
		
class InstanceRunning:

	"""
	Vagrant instance running. Implements :class:`Component`.
	
	:param Instance inst:
	   Managed instance.
	"""
	
	def __init__(self, inst):
	
		self.__inst = inst
		self.__available = None
		
	def available(self, context):
	
		"""
		Check availability.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		:rtype:
		   bool
		:return:
		   Availability value.
		"""
		
		if self.__available is None:
			self.__available = self.__inst.state(context) == "running"
		return self.__available
		
	def insert(self, context):
	
		"""
		Run instance.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		self.__inst.write(context, [
			"up"
		])
		
	def delete(self, context):
	
		"""
		Stop instance.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		self.__inst.write(context, [
			"halt"
		])

