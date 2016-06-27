def print_loop(the_list):
	for each in the_list:
		if isinstance(each, list):
			print_loop(each)
		else:
			print(each)
