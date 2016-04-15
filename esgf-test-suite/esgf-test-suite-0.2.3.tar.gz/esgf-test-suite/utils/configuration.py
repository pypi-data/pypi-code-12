import os
import sys
import site
import inspect
import subprocess

from ConfigParser import SafeConfigParser

def read_config():
	modulePath = os.path.abspath(inspect.getsourcefile(lambda _: None))
	configPath = modulePath.rsplit('/', 2)[0]+'/configuration.ini'

	parser = SafeConfigParser()

	parser.readfp(open(configPath))
	config = dict((section, dict((option, parser.get(section, option))
                             for option in parser.options(section)))
              for section in parser.sections())	
	return config
