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

class Set:

	"""
	Resource set. Implements :class:`Component`.
	
	:param str source_path:
	   Path relative to base directory.
	:param str target_path:
	   Path relaltive to profile working directory.
	:param dict props:
	   Resource properties. Property with name ``context`` is reserved.
	"""
	
	def __init__(self, source_path, target_path, props):
	
		if os.path.isabs(source_path):
			msg = "Source path '{}' is absolute"
			raise Exception(msg.format(source_path))
		self.__source_path = source_path
		
		if os.path.isabs(target_path):
			msg = "Target path '{}' is absolute"
			raise Exception(msg.format(target_path))
		self.__target_path = target_path
		
		self.__props = props
		
	def __repr__(self):
	
		return "{}.{}({}, {}, {})".format(
			self.__module__,
			type(self).__name__,
			repr(self.__source_path),
			repr(self.__target_path),
			repr(self.__props)
		)
		
	def __resolve(self, context, in_path, out_path):
	
		try:
			if os.path.basename(in_path)[0] != ".":
				if os.path.isfile(in_path):
					in_file = open(in_path, "r")
					out_file = open(out_path, "w")
					resolver = Resolver(context, out_file, self.__props)
					c = in_file.read(1)
					while len(c) > 0:
						resolver.update(c)
						c = in_file.read(1)
					in_file.close()
					out_file.close()
				elif os.path.isdir(in_path):
					if not os.path.exists(out_path):
						os.makedirs(out_path)
					for fname in os.listdir(in_path):
						self.__resolve(
							context,
							os.path.join(in_path, fname),
							os.path.join(out_path, fname)
						)
		except:
			print("Error resolving '{}'".format(in_path))
			raise
			
	def available(self, context):
	
		"""
		Return ``None``.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		return None
		
	def insert(self, context):
	
		"""
		Resolve resoures.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		in_path = os.path.join(context.base_dir(), self.__source_path)
		out_path = os.path.join(context.profile_dir(), self.__target_path)
		self.__resolve(context, in_path, out_path)
		
	def delete(self, context):
	
		"""
		Does nothing.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		pass
		
class Resolver:

	"""
	Resolve text resource variables.
	
	:param r_out:
	   Resolver output.
	:param dict r_vars:
	   Resolver variables. Variable with name ``context`` is reserved.
	"""
	
	def __init__(self, context, r_out, r_vars):
	
		self.__context = context
		self.__r_out = r_out
		self.__r_vars = r_vars
		self.__r_vars["context"] = self.__context
		self.__expr = io.StringIO()
		self.__update = self.__update_plain
		
	def __update_plain(self, c):
	
		if c == '#':
			self.__update = self.__update_sharp
		else:
			self.__r_out.write(c)
			
	def __update_sharp(self, c):
	
		if c == '{':
			self.__update = self.__update_expr
		else:
			if c == '#':
				self.__update = self.__update_sharpn
			else:
				self.__update = self.__update_plain
				self.__r_out.write('#')
			self.__r_out.write(c)
			
	def __update_sharpn(self, c):
	
		if c != '#':
			self.__update = self.__update_plain
		self.__r_out.write(c)
		
	def __update_expr(self, c):
	
		if c == '}':
			self.__update = self.__update_plain
			self.__resolve()
		else:
			if c == '\'':
				self.__update = self.__update_expr_quot
			self.__expr.write(c)
			
	def __update_expr_quot(self, c):
	
		if c == '\'':
			self.__update = self.__update_expr
		self.__expr.write(c)
		
	def __resolve(self):
	
		resolver = Resolver(self.__context, self.__r_out, self.__r_vars)
		self.__expr.seek(0)
		for c in eval(self.__expr.read(), {}, self.__r_vars):
			resolver.update(c)
		self.__expr = io.StringIO()
		
	def update(self, c):
	
		"""
		Update output with next character.
		
		:param str c:
		   Next character.
		"""
		
		self.__update(c)

