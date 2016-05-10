#!usr/bin/python
def print_list(the_list,level):
	for x in the_list:
		if isinstance(x,list):
			print_list(x,level+1)
		else:
			for tab in range(level):
				print ("\t",end='')
			print(x)








