'''
created		:	02-JUL-2016
author		:	kneerunjun@gmail.com
description	:	solves the recursion of lists
'''

def recurse_list(toRead,flat=True,indent=0):
	if(isinstance(toRead, list)):
		#this is when we have to recurse the list further
		for item in toRead:
			if (isinstance(item, list)):		
				recurse_list(item, flat,indent+1)
			else:
				if flat==False:	
					for item in range(indent):
						print("\t", end='')
				print(toRead)
			#thats about it!
	else:
		print("first parameter has to be a list")
		#is the case when toRead itself is not alist
		
