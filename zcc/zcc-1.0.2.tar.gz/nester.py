#!usr/bin/python
def print_list(the_list,indent=false,level=0):
	for x in the_list:
		if isinstance(x,list):
			print_list(x,indent,level+1)
		else:
			"""if indent:
				for tab in range(level):
					print ("\t",end='')"""
			if indent:
					print ("\t"*level,end='')
			print(x)








