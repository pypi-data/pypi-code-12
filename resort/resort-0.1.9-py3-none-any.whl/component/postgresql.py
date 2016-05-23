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
import psycopg2

class Connection:

	"""
	PostgreSQL database connection.
	
	:param str host:
	   Database host.
	:param int port:
	   Database port.
	:param str dbname:
	   Database name.
	:param str username:
	   Database user name.
	:param str password:
	   Database password.
	"""
	
	def __init__(self, host, port, dbname, username, password):
	
		self.__host = host
		self.__port = port
		self.__dbname = dbname
		self.__username = username
		self.__password = password
		
	def __connect(self):
	
		return psycopg2.connect(
			host=self.__host,
			port=self.__port,
			database=self.__dbname,
			user=self.__username,
			password=self.__password,
			connect_timeout=20.
		)
		
	def execute(self, script):
	
		"""
		Execute script.
		
		:param str script:
		   Script to be executed.
		"""
		
		try:
			conn = self.__connect()
			conn.cursor().execute(script)
			conn.commit()
		finally:
			conn.close()
			
	def database_changes(self, script_path):
	
		"""
		Create a database changes component.
		
		:param str script_path:
		   Path of script file.
		:rtype:
		   DatabaseChanges
		:return:
		   Database changes component.
		"""
		
		return DatabaseChanges(self, script_path)
		
class DatabaseChanges:

	"""
	Database changes. Implements :class:`Component`.
	
	:param Connection conn:
	   Target connection.
	:param str script_path:
	   Script path.
	"""
	
	def __init__(self, conn, script_path):
	
		self.__conn = conn
		self.__script_path = script_path
		
	def __preprocess(self, src_path, out):
	
		exec_prefix = "exec '"
		base_dir = os.path.dirname(src_path)
		
		src_file = open(src_path, "r")
		for line in src_file.readlines():
			strip_line = line.strip()
			if strip_line.startswith(exec_prefix):
				exec_path = strip_line[len(exec_prefix):-1]
				self.__preprocess(os.path.join(base_dir, exec_path), out)
			elif len(strip_line) > 0:
				out.write("{}\n".format(strip_line))
		src_file.close()
		
	def available(self, context):
	
		"""
		Always returns ``None``.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		return None
		
	def insert(self, context):
	
		"""
		Applies database changes.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		buf = io.StringIO()
		self.__preprocess(os.path.join(context.base_dir(),
				self.__script_path), buf)
		buf.seek(0)
		self.__conn.execute(buf.read())
		
	def delete(self, context):
	
		"""
		Does nothing.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		pass

