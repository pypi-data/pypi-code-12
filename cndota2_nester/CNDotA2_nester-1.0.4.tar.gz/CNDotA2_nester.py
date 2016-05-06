"""This is a function to print elements of a list and its nested lists, and you can add tabs before every elements"""
def print_lol(the_list, level = 0):
	for each_item in the_list:
		"""If the item is a list, then call the function again, if
                   the item is already an element, then print it directly"""
		if isinstance(each_item, list):
			print_lol(each_item, level + 1)
		else:
			for tab_stop in range(level):
				print("\t", end="")
			print(each_item)
