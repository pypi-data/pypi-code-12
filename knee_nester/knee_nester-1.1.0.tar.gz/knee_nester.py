'''
created		:	02-JUL-2016
author		:	kneerunjun@gmail.com
description	:	solves the recursion of lists
'''

def recurse_list(toRead,indent):
	if(isinstance(toRead, list)):
		#this is when we have to recurse the list further
		for item in toRead:
			recurse_list(item, indent+1)
	else:
		for item in range(indent):
			print("\t", end='')
		print(toRead)
		#thats about it!

