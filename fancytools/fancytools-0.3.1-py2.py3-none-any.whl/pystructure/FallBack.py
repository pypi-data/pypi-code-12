# -*- coding: utf-8 -*-

import sys


class FallBack(object):
	'''
	a class allowing to automatically using another module as fall back
	if the given module doesn't have a needed attribute
	
	to create the fall back compatibility just ad the following line to your module:
	
	>>> FallBack(__name__, MyFallBackModule, print_warning=True)
	'''

	def __init__(self, ownModuleName, fallbackModule, print_warning=True):
		
		self.wrappedModule = sys.modules[ownModuleName]
		self.fallbackModule = fallbackModule
		self.print_warning = print_warning
		self._print_waring_is_callable = callable(self.print_warning)
		#register Fallback-wrapper in sys:
		sys.modules[ownModuleName] = self


	def __getattr__(self, name):
		try:
			return getattr(self.wrappedModule, name)
		except AttributeError:
			if (not self._print_waring_is_callable and self.print_warning) or self.print_warning():				
				print 'WARING: no %s class exists for %s yet ... continue using fallback' %(
					self.wrappedModule.__name__,name)
			return getattr(self.fallbackModule, name)
