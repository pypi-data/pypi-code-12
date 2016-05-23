def print_list(list_data):
	for data in list_data:
		if isinstance(data,list):
			print_list(data)
		else:
			print(data)
