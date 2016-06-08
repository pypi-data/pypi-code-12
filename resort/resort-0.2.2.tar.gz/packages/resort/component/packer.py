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
import shutil
import subprocess

class Image:

	"""
	Packer image.
	
	:param Contextual base_dir:
	   Template base directory.
	:param Contextual template_path:
	   Template file path relative to ``base_dir``.
	"""
	
	def __init__(self, base_dir, template_path):
	
		self.__base_dir = base_dir
		self.__template_path = template_path
		
	def __repr__(self):
	
		return "{}.{}({}, {})".format(
			self.__module__,
			type(self).__name__,
			repr(self.__base_dir),
			repr(self.__template_path)
		)
		
	def available(self, context):
	
		"""
		Always return ``None``.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		return None
		
	def insert(self, context):
	
		"""
		Build the image.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		try:
			current_dir = os.getcwd()
			os.chdir(context.resolve(self.__base_dir))
			args = [
				"packer",
				"build",
				context.resolve(self.__template_path)
			]
			subprocess.call(args)
		finally:
			shutil.rmtree("output-*", ignore_errors=True)
			os.chdir(current_dir)
		
	def delete(self, context):
	
		"""
		Does nothing.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		pass

