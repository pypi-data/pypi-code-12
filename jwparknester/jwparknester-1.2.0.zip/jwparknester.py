def print_lol(t_list, level=0):
	for p in t_list:
		if isinstance(p, list):
			print_lol(p, level+1)
		else:
			for tab in range(level):
				print("\t", end='')
			print(p)


