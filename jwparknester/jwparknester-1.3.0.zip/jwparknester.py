def print_lol(t_list, indent=False, level=0):
	for p in t_list:
		if isinstance(p, list):
			print_lol(p, indent, level+1)
		else:
			if indent:
				for tab in range(level):
					print("\t", end='')
			print(p)


