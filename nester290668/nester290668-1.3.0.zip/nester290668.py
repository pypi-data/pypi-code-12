"""This is the "nester.py" module, and it provides one function called print_lol()
which prints lists that may or may not include nested lists.
A second argument called “indent" is used to switch between indentation or no indentation
A third argument called “level" is used to insert tab-stops when a nested list is encountered"""

def print_lol(the_list, indent=False, level=0):
	"""This function takes a positional argument called "the_list", which is any
	Python list (of, possibly, nested lists). Each data item in the provided list
	is (recursively) printed to the screen on its own line."""
                
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item, indent, level+1)
		else:
			if indent:
				for tab_stop in range(level):
					print("\t" * level, end='')
			print(each_item)
