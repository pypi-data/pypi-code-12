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

import os
import subprocess

class Project:

	"""
	Maven project. Implements :class:`Component`.
	
	:param Contextual base_dir:
	   Project base directory.
	:param bool dependency:
	   Project must be installed or only packaged.
	"""
	
	def __init__(self, base_dir, dependency=False):
	
		self.__base_dir = base_dir
		self.__dependency = dependency
		
	def __repr__(self):
	
		return "{}.{}({}, {})".format(
			self.__module__,
			type(self).__name__,
			repr(self.__base_dir)
		)
		
	def __execute(self, context, phase):
	
		subprocess.call([
			"mvn",
			"-f",
			os.path.join(os.path.join(context.resolve(self.__base_dir),
					"pom.xml")),
			phase
		])
		
	def available(self, context):
	
		"""
		Always return ``None``.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		return None
		
	def insert(self, context):
	
		"""
		Build the project.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		if self.__dependency:
			self.__execute(context, "install")
		else:
			self.__execute(context, "package")
		
	def delete(self, context):
	
		"""
		Does nothing.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		self.__execute(context, "clean")

