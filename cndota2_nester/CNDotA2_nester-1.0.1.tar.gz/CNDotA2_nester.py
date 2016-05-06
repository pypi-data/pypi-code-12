"""This is a function to print elements of a list and its nested lists"""
def print_lol(the_list):
	for each_item in the_list:
		"""If the item is a list, then call the function again, if
                   the item is already an element, then print it directly"""
		if isinstance(each_item, list):
			print_lol(each_item)
		else:
			print(each_item)
