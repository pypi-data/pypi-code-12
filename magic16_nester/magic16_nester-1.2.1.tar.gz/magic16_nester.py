"""this is the "nester.py" module and it provides one function called print_lol() which prints lists that may or may not include nested lists."""
def print_lol(the_list,indent = False, level = 0):
	"""This function takes three positional argument called "the_list", "indent" and "level", the_list which is any Python list (of-possibly-nested list). Each item in the provided list (recursively) print to the screen on its own line.indent is a boolean switcher"""

	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item, indent, level + 1)
		else:
			if indent:
				for tab_stop in range(level):
					print("\t", end=' ')
			print(each_item)


