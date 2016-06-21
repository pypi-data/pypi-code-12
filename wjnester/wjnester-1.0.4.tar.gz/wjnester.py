def print_lol(the_list,level):
	for each in the_list:
		if isinstance(each,list):
			print_lol(each,level+1)
		else:
            for tap_stop in range(level):
                print("\t",end='')
			print(each)
