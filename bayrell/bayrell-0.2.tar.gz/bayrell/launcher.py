# -*- coding: utf-8 -*-
#
# Bayrell Application Server

import subprocess
from foruse import *

class Launcher(log.Log):
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		self.enable = False
		self.api_name = ""
		self.cmd = ""
		self.launcher = ""
		self.params = ""
		self.app_server = None
	
	
	def assign(self, arr):
		keys=[
			'cmd',
			'launcher',
			'params',
		]
		for key in keys:
			val = xarr(arr, key)
			setattr(self, key, val)
			#print ("%s = %s" % (key, val))
		#!endfor
	#!enddef assign
	
	
	def start(self, app, is_wait=False):
		
		try:
			if is_wait:
				cmd = "%(cmd)s %(launcher)s --app-config=%(app_config)s --server-config=%(server_config)s --wait start" 
			else:
				cmd = "%(cmd)s %(launcher)s --app-config=%(app_config)s --server-config=%(server_config)s start" 

			cmd = cmd % {
				'cmd': self.cmd,
				'launcher': self.launcher,
				'app_config' : app.config_path,
				'server_config' : self.app_server.config_path,
				'is_wait' : is_wait,
			}
			
			#print (cmd)
			
			if is_wait == True:
				proc = subprocess.Popen(
					cmd, 
					#env=env, 
					shell=True,
					#stdout=open(os.devnull, 'wb'),
					#stderr=open(os.devnull, 'wb'),
				)
				
				try:
					proc.communicate()
				except KeyboardInterrupt:
					pass
				
			else:
				self._log.info('Start app "%s"' % (app.api_name))
				
				proc = subprocess.Popen(
					cmd, 
					#env=env, 
					shell=True,
					stdout=open(os.devnull, 'wb'),
					stderr=open(os.devnull, 'wb'),
				)
			
		finally:
			# Write pid to file
			"""
			pid_file_path = join_paths(self.directory, 'container.pid')
			file = open(pid_file_path, 'w')
			file.write(str(proc.pid))
			file.close()
			"""
			pass
	#!enddef start
	
#!endclass Launcher