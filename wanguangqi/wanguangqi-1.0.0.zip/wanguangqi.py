def print_lol(the_list,level=0):
	for a in the_list:
		if isinstance(a,list):
			print_lol(a,level+1)
		else:
                        for tab in range(level):
                                print"\t"
			print(a)
