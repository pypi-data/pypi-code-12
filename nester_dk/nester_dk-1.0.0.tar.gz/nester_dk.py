def printlol(the_list):
	for each_item in the_list:
		if isinstance(each_item, list):
			printlol(each_item)
		else:
			print(each_item)