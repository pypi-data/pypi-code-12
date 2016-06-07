def print_movie(the_list):
	for each_movie in the_list:
		if isinstance(each_movie,list):
			print_movie(each_movie)
		else:
			print(each_movie)