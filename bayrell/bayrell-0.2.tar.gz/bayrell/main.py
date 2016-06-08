# -*- coding: utf-8 -*-
#
# Bayrell Application Server

import time
import bayrell
import uvloop
import asyncio
import sys
import os
from foruse import *
from foruse.configparser import ConfigParser
from .proxy import HTTPProxyServer
from .app import Application
from .launcher import Launcher

	
class BayrellServer(log.Log):
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		self.config_data = None
		self.config_path = ""
		
		# Папка, где лежит server.conf
		self.configs_dir = ""
		
		# Настройки http
		self.default_servername = "0.0.0.0"
		self.default_http_port = "8080"
		self.default_https_port = "8443"
		
		# Список всех контейнеров
		self.applications = {}
		
		# Список поддерживаемых загрузчиков
		self.launchers = {}
		
		self.name = ""
		self.apps_work_dir = ""
		
		# Параметры, которые нужно считать из файла конфигурации
		self.config_params = [ 
			'name', 
			'apps_work_dir', 
			'default_servername', 
			'default_http_port', 
			'default_https_port', 
		]
		
	#!enddef __init__
	
	def format(self, s):
		params = {
			'configs_dir': self.configs_dir,
		}
		
		for key in self.config_params:
			params[key] = getattr(self, key)
		
		s = str(s)
		for key, value in xitems(params):
			s = s.replace('%'+key+'%', value)
			
		return s
	
	def get_launcher(self, name):
		return self.launchers.get(name)
	
	def get_app(self, api_name):
		return self.applications.get(api_name)
	
	# Функция возвращает контейнер по его path
	def find_app(self, url):
		
		url = clone(url)
		
		
		def find(applications, search_url):
			#print ('---------')
			#print (search_url)
			find_app = None
			find_route = None
			max_len = -1
			
			for application in xvalues(applications):
				for route in application.routes:
					
					#print (route)
					
					pos = search_url.find(route)
					if pos != -1:
						if len(route) > max_len:
							max_len = len(route)
							find_app = application
							find_route = urlparse2(route)
						#!endif
					#!endif
				#!endfor
			#!endfor
			
			return (find_app, find_route)
		#!enddef
		
		find_app, find_route = find(self.applications, str(url))
		if find_app != None:
			return (find_app, find_route)
		
		url.hostname = '0.0.0.0'
		find_app, find_route = find(self.applications, str(url))
		
		return (find_app, find_route)
	#!enddef
	
	
	# -----------------------------------------------------------------------------
	# Чтение конфига
	# -----------------------------------------------------------------------------
		
	def readconfig_data(self, config_path):
		
		self.config_path = config_path
		self.configs_dir = dirname(config_path)
		
		# Пробуем прочитать конфиг
		if file_exists(config_path):
			try:
				self.config_data = ConfigParser()
				self.config_data.set_init({
					'global':{
						'configs_dir': self.configs_dir,
						'launchers_path': join_paths(dirname(bayrell.__file__), 'launchers'),
					}
				})
				
				self.config_data.read(config_path)
			except Exception as e:
				self.config_data = None
				print (get_traceback())
		#!endif
		
		# Конфиг успешно прочитан
		if self.config_data is not None:
			
			for key in self.config_params:
				val = self.config_data.get('main', key, default=getattr(self, key))
				setattr(self, key, val)
				#print ("%s = %s" % (key, val))
			#!endfor
			
			# Какие лаунчеры поддерживаем?
			self.launchers = {}
			res = self.config_data.get('main', 'launchers')
			
			for api_name in res:
				launcher_config = self.config_data.get('launcher', api_name)
				if launcher_config is not None:
					launcher = Launcher()
					launcher.enable = xbool(xarr(launcher_config, 'enable'))
					launcher.api_name = api_name
					launcher.app_server = self
					launcher.assign(launcher_config)
					self.launchers[api_name] = launcher
					#!endif
				#!endif
				
			#!endfor
			
			#print (self.launchers)
			
			# читаем информацию обо всех приложениях
			self.applications={}
			res = self.config_data.get('main', 'apps')
			
			for config_path in res:
				if file_exists(config_path):
					app = Application()
					app.app_server = self
					app.apps_work_dir = self.apps_work_dir
					app.default_servername = self.default_servername
					app.default_http_port = self.default_http_port
					app.default_https_port = self.default_https_port
					app.configs_dir = self.configs_dir
					app.readconfig_data(config_path)
					self.applications[app.api_name] = app
				#!endif
			#!endfor
			
			#print (self.applications)
			
		#!endif
	#!enddef readconfig_data
	
	
	# -----------------------------------------------------------------------------
	# Start/Stop
	# -----------------------------------------------------------------------------
	
	def start(self, start_apps=False):
		if self.config_data is None:
			self._log.critical('Config error. Terminated')
			sys.exit()
		
		if len(self.applications) == 0:
			self._log.critical('Applications does not exists')
			sys.exit()
		
		if start_apps:
			for app in self.applications:
				app.start()
		
		"""
		ips = []
		for app in self.applications:
			for route in app.routes:
				#ip = (url.hostname, url.port)
				#if not ip in ips:
				#	ips.append(ip)
		"""
		ips = [(self.default_servername, self.default_http_port)]
		loop = asyncio.get_event_loop()
		for ip in ips:
			self._log.info('Start server on %s:%s' % (ip[0], ip[1]))
			f = loop.create_server(
				lambda: HTTPProxyServer(app_server=self, loop=loop),
				ip[0], ip[1]
			)
			asyncio.ensure_future(f)
		#!endfor
		
	#!enddef main_loop
	
	
	def stop(self, stop_apps=False):
		loop = asyncio.get_event_loop()
		
		if stop_apps:
			for app in self.applications:
				app.stop()
		
		
		loop.stop()
		
		#server.close()
		#loop.run_until_complete(server.wait_closed())
		#loop.close()
		
		sec = 0
		if sec != 0:
			print ('Sleep %s sec' % (sec))
			time.sleep(sec)
	#!enddef stop
	
	
	def run(self, start_apps=False):
		loop = asyncio.get_event_loop()
		self.start(start_apps)
		try:
			loop.run_forever()
			pass
		except KeyboardInterrupt:
			self.stop(start_apps)
			
			print('interrupted!')
			pass
	#!enddef run
	
#!endclass BayrellServer
	
	
# Main Applcation Server
main_app_server=None
main_app_config='/etc/bayrell/server.conf'

def get_app_server():
	return main_app_server
#!enddef


def set_app_server(value):
	main_app_server = value
#!enddef

	
def create_app_server():
	global main_app_server
	
	if main_app_server is not None:
		return main_app_server
	
	main_app_server = BayrellServer()
	main_app_server.readconfig_data(main_app_config)
	
	return main_app_server
#!enddef


def start_server(start_apps=False):
	app_server = create_app_server()
	app_server.run(start_apps)
#!enddef	


def stop_server(stop_apps=False):
	app_server = create_app_server()
	app_server.stop(stop_apps)
#!enddef	


def start_app(app_name, is_wait=False):
	app_server = create_app_server()
	app = app_server.get_app(app_name)
	if app is None:
		log.critical('Application %s not found' %(app_name))
	else:
		app.start(is_wait)
#!enddef


def stop_app(app_name):
	app_server = create_app_server()
	app = app_server.get_app(app_name)
	if app is None:
		log.critical('Application %s not found' %(app_name))
	else:
		app.stop()
#!enddef