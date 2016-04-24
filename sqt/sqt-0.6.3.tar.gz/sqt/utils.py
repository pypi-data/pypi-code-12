import os
import re

def available_cpu_count():
	"""
	Number of available virtual or physical CPUs on this system.

	Adapted from http://stackoverflow.com/a/1006301/715090
	"""
	# cpuset may restrict the number of available processors
	try:
		m = re.search(r'(?m)^Cpus_allowed:\s*(.*)$',
						open('/proc/self/status').read())
		if m:
			res = bin(int(m.group(1).replace(',', ''), 16)).count('1')
			if res > 0:
				return res
	except IOError:
		pass

	try:
		import multiprocessing
		return multiprocessing.cpu_count()
	except (ImportError, NotImplementedError):
		pass
	return 1
