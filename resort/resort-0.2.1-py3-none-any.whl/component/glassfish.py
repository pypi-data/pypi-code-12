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

import json
import requests
import urllib

class Endpoint:

	"""
	GlassFish domain management.
	
	:param str host:
	   Endpoint host.
	:param int port:
	   Endpoint port.
	:param str username:
	   Endpoint username.
	:param str password:
	   Endpoint password.
	"""
	
	def __init__(self, host, port, username, password):
	
		self.__base_uri = "https://{}:{}/management/domain".format(host, port)
		self.__username = username
		self.__password = password
		
	def __res_uri(self, path):
	
		return "{}{}".format(self.__base_uri, path)
		
	def __headers(self):
	
		return {
			"Accept": "application/json",
			"X-Requested-By": "GlassFish REST HTML interface"
		}
		
	def __auth(self):
	
		return requests.auth.HTTPBasicAuth(self.__username, self.__password)
		
	def get(self, res_path, timeout=10.):
	
		"""
		Get operation.
		
		:param str res_path:
		   Resource path.
		:param float timeout:
		   Timeout in seconds.
		:rtype:
		   tuple
		:return:
		   Tuple with status code and response body.
		"""
		
		resp = requests.get(
			self.__res_uri(res_path),
			headers=self.__headers(),
			verify=False,
			auth=self.__auth(),
			timeout=timeout
		)
		return (
			resp.status_code,
			json.loads(resp.text) if resp.status_code == 200 else {}
		)
		
	def post(self, res_path, data=None, files=None, timeout=10.):
	
		"""
		Post operation.
		
		:param str res_path:
		   Resource path.
		:param list data:
		   Request parameters for data.
		:param list files:
		   Request parameters for files.
		:param float timeout:
		   Timeout in seconds.
		:rtype:
		   tuple
		:return:
		   Tuple with status code and response body.
		"""
		
		resp = requests.post(
			self.__res_uri(res_path),
			data=data,
			files=files,
			headers=self.__headers(),
			verify=False,
			auth=self.__auth(),
			timeout=timeout
		)
		return (
			resp.status_code,
			json.loads(resp.text)
		)
		
	def delete(self, res_path, timeout=10.):
	
		"""
		Delete operation.
		
		:param str res_path:
		   Resource path.
		:param float timeout:
		   Timeout in seconds.
		:rtype:
		   tuple
		:return:
		   Tuple with status code and response body.
		"""
		
		resp = requests.delete(
			self.__res_uri(res_path),
			headers=self.__headers(),
			verify=False,
			auth=self.__auth(),
			timeout=timeout
		)
		return (
			resp.status_code,
			json.loads(resp.text) if resp.status_code == 200 else {}
		)
		
class Domain:

	"""
	Domain for an endpoint. Implements :class:`Component`.
	
	:param Endpoint endpoint:
	   Domain endpoint.
	:param float avail_timeout:
	   Availability check timeout in seconds.
	"""
	
	def __init__(self, endpoint, avail_timeout):
	
		self.__endpoint = endpoint
		self.__avail_timeout = avail_timeout
		self.__available = None
		
	def available(self, context):
	
		"""
		Domain availability.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		try:
			if self.__available is None:
				status_code, msg = self.__endpoint.get("")
				self.__available = status_code == 200
		except:
			self.__available = False
			
		return self.__available
		
	def insert(self, context):
	
		"""
		Wait domain to be available.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		:raise Exception:
		   Domain could not been inserted.
		"""
		
		status_code, msg = self.__endpoint.get("", self.__avail_timeout)
		if status_code != 200:
			raise Exception("GlassFish domain could not been inserted")
		self.__available = True
		
	def delete(self, context):
	
		"""
		Does nothing.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		self.__available = None
		
	def application(self, name, context_root, path):
	
		"""
		Domain application.
		
		:param str name:
		   Application name.
		:param str context_root:
		   Appliaction context root. May be ``None``.
		:param Contextual path:
		   File path.
		:rtype:
		   Application
		"""
		
		return Application(self.__endpoint, name, context_root, path)
		
	def jdbc_resource(self, name, pool_name):
	
		"""
		Domain JDBC resource.
		
		:param str name:
		   Resource name.
		:param str pool_name:
		   Resource pool name.
		:rtype:
		   JDBCResource
		"""
		
		return JDBCResource(self.__endpoint, name, pool_name)
		
	def connector_resource(self, name, pool_name):
	
		"""
		Domain connector resource.
		
		:param str name:
		   Resource name.
		:param str pool_name:
		   Resource pool name.
		:rtype:
		   ConnectorResource
		"""
		
		return ConnectorResource(self.__endpoint, name, pool_name)
		
	def mail_session(self, name, host, username, mail_from, props):
	
		"""
		Domain mail session.
		
		:param str name:
		   Mail session name.
		:param str host:
		   Mail host.
		:param str username:
		   Mail username.
		:param str mail_from:
		   Mail "from" address.
		:param dict props:
		   Extra properties.
		:rtype:
		   MailSession
		"""
		
		return MailSession(self.__endpoint, name, host, username, mail_from,
				props)
		
	def custom_resource(self, name, restype, factclass, props):
	
		"""
		Domain custom resource.
		
		:param str name:
		   Resource name.
		:param str restype:
		   Resource type.
		:param str factclass:
		   Resource factory class.
		:param dict props:
		   Resource properties.
		:rtype:
		   CustomResource
		"""
		
		return CustomResource(self.__endpoint, name, restype, factclass, props)
		
	def jdbc_connection_pool(self, name, res_type, ds_classname, props):
			
		"""
		Domain JDBC connection pool.
		
		:param str name:
		   Resource name.
		:param str res_type:
		   Resource type.
		:param str ds_classname:
		   Data source class name.
		:param dict props:
		   Connection pool properties.
		:rtype:
		   JDBCConnectionPool
		"""
		
		return JDBCConnectionPool(self.__endpoint, name, res_type,
				ds_classname, props)
				
	def connector_connection_pool(self, name, res_adapter_name, conn_def_name,
			props):
			
		"""
		Domain connector connection pool.
		
		:param str name:
		   Resource name.
		:param str res_adapter_name:
		   Resource adapter name.
		:param str conn_def_name:
		   Resource connection definition name.
		:param dict props:
		   Connection pool properties.
		:rtype:
		   ConnectorConnectionPool
		"""
		
		return ConnectorConnectionPool(self.__endpoint, name, res_adapter_name,
				conn_def_name, props)
		
class Application:

	"""
	Domain application. Implements :class:`Component`.
	
	:param Endpoint endpoint:
	   Domain endpoint.
	:param str name:
	   Application name.
	:param str context_root:
	   Appliaction context root. May be ``None``.
	:param Contextual path:
	   File path.
	"""
	
	def __init__(self, endpoint, name, context_root, path):
	
		self.__endpoint = endpoint
		self.__name = name
		self.__context_root = context_root
		self.__path = path
		self.__available = None
		
	def available(self, context):
	
		"""
		Application availability.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		try:
			if self.__available is None:
				encoded_name = urllib.parse.quote_plus(self.__name)
				status_code, msg = self.__endpoint.get(
					"/applications/application/{}".format(encoded_name)
				)
				self.__available = status_code == 200
		except:
			self.__available = False
			
		return self.__available
		
	def insert(self, context):
	
		"""
		Deploy application.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		module_file = open(context.resolve(self.__path), "rb")
		data = {
			"name": self.__name
		}
		if self.__context_root is not None:
			data["contextroot"] = self.__context_root
		status_code, msg = self.__endpoint.post(
			"/applications/application",
			data=data,
			files={
				"id": module_file
			},
			timeout=60.
		)
		module_file.close()
		self.__available = True
		
	def delete(self, context):
	
		"""
		Undeploy application.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		status_code, msg = self.__endpoint.delete(
			"/applications/application/{}".format(self.__name)
		)
		self.__available = False
		
class JDBCResource:

	"""
	JDBC resource. Implements :class:`Component`.
	
	:param Endpoint endpoint:
	   Domain endpoint.
	:param str name:
	   Resource name.
	:param str pool_name:
	   Resource pool name.
	"""
	
	def __init__(self, endpoint, name, pool_name):
	
		self.__endpoint = endpoint
		self.__name = name
		self.__pool_name = pool_name
		self.__available = None
		
	def available(self, context):
	
		"""
		Resource availability.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		try:
			if self.__available is None:
				encoded_name = urllib.parse.quote_plus(self.__name)
				status_code, msg = self.__endpoint.get(
					"/resources/jdbc-resource/{}".format(encoded_name)
				)
				self.__available = status_code == 200
		except:
			self.__available = False
			
		return self.__available
		
	def insert(self, context):
	
		"""
		Create resource.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		status_code, msg = self.__endpoint.post(
			"/resources/jdbc-resource",
			data={
				"id": self.__name,
				"poolName": self.__pool_name
			}
		)
		self.__available = True
		
	def delete(self, context):
	
		"""
		Remove resource.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		encoded_name = urllib.parse.quote_plus(self.__name)
		status_code, msg = self.__endpoint.delete(
			"/resources/jdbc-resource/{}".format(encoded_name)
		)
		self.__available = False
		
class ConnectorResource:

	"""
	Connector resource. Implements :class:`Component`.
	
	:param Endpoint endpoint:
	   Domain endpoint.
	:param str name:
	   Resource name.
	:param str pool_name:
	   Resource pool name.
	"""
	
	def __init__(self, endpoint, name, pool_name):
	
		self.__endpoint = endpoint
		self.__name = name
		self.__pool_name = pool_name
		self.__available = None
		
	def available(self, context):
	
		"""
		Resource availability.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		try:
			if self.__available is None:
				encoded_name = urllib.parse.quote_plus(self.__name)
				status_code, msg = self.__endpoint.get(
					"/resources/connector-resource/{}".format(encoded_name)
				)
				self.__available = status_code == 200
		except:
			self.__available = False
			
		return self.__available
		
	def insert(self, context):
	
		"""
		Create resource.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		status_code, msg = self.__endpoint.post(
			"/resources/connector-resource",
			data={
				"id": self.__name,
				"poolname": self.__pool_name
			}
		)
		self.__available = True
		
	def delete(self, context):
	
		"""
		Remove resource.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		encoded_name = urllib.parse.quote_plus(self.__name)
		status_code, msg = self.__endpoint.delete(
			"/resources/connector-resource/{}".format(encoded_name)
		)
		self.__available = False
		
class MailSession:

	"""
	Mail session. Implements :class:`Component`.
	
	:param Endpoint endpoint:
	   Domain endpoint.
	:param str name:
	   Mail session name.
	:param str host:
	   Mail host.
	:param str username:
	   Mail username.
	:param str mail_from:
	   Mail "from" address.
	:param dict props:
	   Extra properties.
	"""
	
	def __init__(self, endpoint, name, host, username, mail_from, props):
	
		self.__endpoint = endpoint
		self.__name = name
		self.__host = host
		self.__username = username
		self.__mail_from = mail_from
		self.__props = props
		self.__available = None
		
	def available(self, context):
	
		"""
		Mail session availability.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		try:
			if self.__available is None:
				encoded_name = urllib.parse.quote_plus(self.__name)
				status_code, msg = self.__endpoint.get(
					"/resources/mail-resource/{}".format(encoded_name)
				)
				self.__available = status_code == 200
		except:
			self.__available = False
			
		return self.__available
		
	def insert(self, context):
	
		"""
		Create mail session.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		status_code, msg = self.__endpoint.post(
			"/resources/mail-resource",
			data={
				"id": self.__name,
				"host": self.__host,
				"user": self.__username,
				"from": self.__mail_from,
				"property": props_value(self.__props)
			}
		)
		self.__available = True
		
	def delete(self, context):
	
		"""
		Remove mail session.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		encoded_name = urllib.parse.quote_plus(self.__name)
		status_code, msg = self.__endpoint.delete(
			"/resources/mail-resource/{}".format(encoded_name)
		)
		self.__available = False
		
class CustomResource:

	"""
	Domain resource. Implements :class:`Component`.
	
	:param Endpoint endpoint:
	   Domain endpoint.
	:param str name:
	   Resource name.
	:param str restype:
	   Resource type.
	:param str factclass:
	   Resource factory class.
	:param dict props:
	   Resource properties.
	"""
	
	def __init__(self, endpoint, name, restype, factclass, props):
	
		self.__endpoint = endpoint
		self.__name = name
		self.__restype = restype
		self.__factclass = factclass
		self.__props = props
		self.__available = None
		
	def available(self, context):
	
		"""
		Resource availability.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		try:
			if self.__available is None:
				encoded_name = urllib.parse.quote_plus(self.__name)
				status_code, msg = self.__endpoint.get(
					"/resources/custom-resource/{}".format(encoded_name)
				)
				self.__available = status_code == 200
		except:
			self.__available = False
			
		return self.__available
		
	def insert(self, context):
	
		"""
		Create resource.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		status_code, msg = self.__endpoint.post(
			"/resources/custom-resource",
			data={
				"id": self.__name,
				"restype": self.__restype,
				"factoryclass": self.__factclass,
				"property": props_value(self.__props)
			}
		)
		self.__available = True
		
	def delete(self, context):
	
		"""
		Remove resource.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		encoded_name = urllib.parse.quote_plus(self.__name)
		status_code, msg = self.__endpoint.delete(
			"/resources/custom-resource/{}".format(encoded_name)
		)
		self.__available = False
		
class JDBCConnectionPool:

	"""
	JDBC connection pool. Implements :class:`Component`.
	
	:param Endpoint endpoint:
	   Domain endpoint.
	:param str name:
	   Resource name.
	:param str res_type:
	   Resource type.
	:param str ds_classname:
	   Data source class name.
	:param dict props:
	   Connection pool properties.
	"""
	
	def __init__(self, endpoint, name, res_type, ds_classname, props):
	
		self.__endpoint = endpoint
		self.__name = name
		self.__res_type = res_type
		self.__ds_classname = ds_classname
		self.__props = props
		self.__available = None
		
	def available(self, context):
	
		"""
		Connection pool availability.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		try:
			if self.__available is None:
				encoded_name = urllib.parse.quote_plus(self.__name)
				status_code, msg = self.__endpoint.get(
					"/resources/jdbc-connection-pool/{}".format(encoded_name)
				)
				self.__available = status_code == 200
		except:
			self.__available = False
			
		return self.__available
		
	def insert(self, context):
	
		"""
		Create connection pool.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		status_code, msg = self.__endpoint.post(
			"/resources/jdbc-connection-pool",
			data={
				"id": self.__name,
				"resType": self.__res_type,
				"datasourceClassname": self.__ds_classname,
				"property": props_value(self.__props)
			}
		)
		self.__available = True
		
	def delete(self, context):
	
		"""
		Remove connection pool.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		encoded_name = urllib.parse.quote_plus(self.__name)
		status_code, msg = self.__endpoint.delete(
			"/resources/jdbc-connection-pool/{}".format(encoded_name)
		)
		self.__available = False
		
class ConnectorConnectionPool:

	"""
	Connector connection pool. Implements :class:`Component`.
	
	:param Endpoint endpoint:
	   Domain endpoint.
	:param str name:
	   Resource name.
	:param str res_adapter_name:
	   Resource adapter name.
	:param str conn_def_name:
	   Resource connection definition name.
	:param dict props:
	   Connection pool properties.
	"""
	
	def __init__(self, endpoint, name, res_adapter_name, conn_def_name, props):
	
		self.__endpoint = endpoint
		self.__name = name
		self.__res_adapter_name = res_adapter_name
		self.__conn_def_name = conn_def_name
		self.__props = props
		self.__available = None
		
	def available(self, context):
	
		"""
		Connection pool availability.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		try:
			if self.__available is None:
				encoded_name = urllib.parse.quote_plus(self.__name)
				status_code, msg = self.__endpoint.get(
					"/resources/connector-connection-pool/{}".format(
							encoded_name)
				)
				self.__available = status_code == 200
		except:
			self.__available = False
			
		return self.__available
			
	def insert(self, context):
	
		"""
		Create connection pool.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		status_code, msg = self.__endpoint.post(
			"/resources/connector-connection-pool",
			data={
				"id": self.__name,
				"resourceAdapterName": self.__res_adapter_name,
				"connectiondefinitionname": self.__conn_def_name,
				"property": props_value(self.__props)
			}
		)
		self.__available = True
		
	def delete(self, context):
	
		"""
		Remove connection pool.
		
		:param resort.engine.execution.Context context:
		   Current execution context.
		"""
		
		encoded_name = urllib.parse.quote_plus(self.__name)
		status_code, msg = self.__endpoint.delete(
			"/resources/connector-connection-pool/{}".format(encoded_name)
		)
		self.__available = False
		
def domain(host, port, username, password, avail_timeout=240.):
	
	"""
	Endpoint domain.
	
	:param str host:
	   Endpoint host.
	:param int port:
	   Endpoint port.
	:param str username:
	   Endpoint username.
	:param str password:
	   Endpoint password.
	:param float avail_timeout:
	   Availability check timeout in seconds.
	:rtype:
	   Domain
	:return:
	   Domain for the given endpoint parameters.
	"""
	
	return Domain(Endpoint(host, port, username, password), avail_timeout)
	
def props_value(props):

	"""
	Properties value.
	
	:param dict props:
	   Properties dictionary.
	:rtype:
	   str
	:return:
	   Properties as string.
	"""
	
	sep = ""
	result_value = ""
	for prop_key, prop_value in props.items():
		result_value = "{}{}{}={}".format(
			result_value,
			sep,
			prop_key,
			prop_value
		)
		sep = ":"
	return result_value

