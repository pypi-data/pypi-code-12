"""This module contains just 
one function called print_lol"""
def print_lol(the_list, tabs = 0):
	"""Print List of List function prints list
	objects and nested list objects. Each 
	data item in the provided list is 
	printed to the screen on it's own line"""
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item, tabs + 1)
		else:
			for num in range(tabs):
				print("\t", end = '')
			print(each_item)
