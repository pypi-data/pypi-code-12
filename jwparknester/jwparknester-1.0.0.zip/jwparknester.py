def print_lol(t_list):
	for p in t_list:
		if isinstance(p, list):
			print_lol(p)
		else:
			print(p)


