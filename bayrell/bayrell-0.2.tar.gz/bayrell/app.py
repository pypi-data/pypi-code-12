# -*- coding: utf-8 -*-
#
# Bayrell Application Server

import bayrell
import configparser
import subprocess
import signal
from foruse import *
import bayrell_app  


class Application(bayrell_app.Application):
	
	def __init__(self, *args, **kwargs):
		super().__init__(self, *args, **kwargs)
		
		self.app_server = None
	#!enddef
	
	
	# Запустить приложение
	def start(self, is_wait=False):
		if not self.enabled:
			return False
		
		if self.is_work():
			self._log.info('App "%s" is already work' % (self.api_name))
			return True
		
		# Запускаем приложение с помощью лаунчера
		launcher = self.app_server.get_launcher(self.launcher)
		if launcher is not None:
			launcher.start(self, is_wait)
			pass
		
		return True
	#!enddef start
	
#!endclass Container