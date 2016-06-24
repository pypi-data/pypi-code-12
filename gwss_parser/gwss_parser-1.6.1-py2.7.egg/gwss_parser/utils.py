"""
This file contains common utilities to be used
by GWSS 
"""

def jjoin(*args):
	"""
	jjoin(a,b,c) -> "a:b:c"
	Create redis namespace
	"""
	return ':'.join([x for x in args])