"""This module prints out the movies in list as nested or whatever chosen"""
def print_movies(argument,level):
	for arg in argument:
		if isinstance(arg,list):
			print_movies(arg,level+1)
		else:
			for tab_stop in range(level):
				print("\t",end='')
			print(arg)
