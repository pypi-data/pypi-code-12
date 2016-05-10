#!usr/bin/python
def print_list(the_list):
	for x in the_list:
		if isinstance(x,list):
			print_list(x)
		else:
			print (x)








