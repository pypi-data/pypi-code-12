"""Head First Python
	My First Python Module """
def print_lol(the_list, level=0):
	"""This function takes a positional argument called "the_list",
		which is any Phthon list (of- possoble - nested lists).
		Each data item in the provided list is (recursively) printed
		to the screen on it's own line.'"""
	for each_item in the_list:
	#for every each_item
		if isinstance(each_item, list):
		#Recursive func call
			print_lol(each_item, level+1)
		else:
			for tab_stop in range(level):
				print("\t", end='')
			print(each_item)