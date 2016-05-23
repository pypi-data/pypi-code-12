def print_list(list_data,level):
	for data in list_data:
		if isinstance(data,list):
			print_list(data,level+1)
		else:
			for tab_stop in range(level):
				print("\t",end='')
			print(data)
