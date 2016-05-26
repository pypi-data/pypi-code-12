"""This Is Module "nesster.py", It Provides A Function Called print_lol(),
	which prints all elements out of a list whichever it is nested or not."""
def print_lol(the_list):
	"""This Function takes "the_list" as a parameter and prints all of its
		elements out, and each elements occupies one row."""
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item)
		else:
			print(each_item)