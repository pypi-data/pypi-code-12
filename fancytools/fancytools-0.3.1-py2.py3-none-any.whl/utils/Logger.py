# -*- coding: utf-8 -*-
from time import gmtime, strftime


class Logger:
	'''
	writes into log-file and on screen at the same time
	
	>>> import sys
	>>> import os
	>>> log_file = file('my_logfile.log', 'w')
	>>> logger = Logger(sys.stdout, log_file)
	>>> sys.stdout = logger
	>>> sys.stderr = logger

	every output will also be saved in file, e.g.
	>>> print 'hello world' #every output will also be saved in file
	hello world

	to prove this we read the log file
	>>> logger.close()
	>>> log_file = open('my_logfile.log', 'r')
	
	>>> logcontent = log_file.read()
	>>> 'hello world' in logcontent
	True
	>>> os.remove('my_logfile.log')
	'''

	def __init__(self, stdout, logfile):
		self.stdout = stdout
		self.logfile = logfile
		self.logfile.write('''

####################################
New run at %s
####################################

''' %strftime( "%d.%m.%Y|%H:%M:%S", gmtime() ) )


	def write(self, text):
		self.stdout.write(text)
		self.logfile.write(text.encode('utf8'))
		self.logfile.flush()


	def close(self):
		"""Does this work or not?"""
		self.stdout.close()
		self.logfile.close()


if __name__ == "__main__":
	import doctest
	doctest.testmod()