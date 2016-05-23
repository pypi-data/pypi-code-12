def print_list(list_data,indent,level=0):
	for data in list_data:
		if isinstance(data,list):
			print_list(data,level+1)
		else:
			if indent:
				for tab_stop in range(level):
					print("\t",end='')
			print(data)
