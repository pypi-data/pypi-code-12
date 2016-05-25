def print_movies (argument):
	for arg in argument:
		if isinstance(arg,list):
			print_movies(arg)
		else:
			print(arg)