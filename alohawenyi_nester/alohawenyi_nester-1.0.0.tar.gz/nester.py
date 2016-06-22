"""This is a function which can print each item of the list"""
def print_lol(the_list):
	"""This is a BIF function of python"""
	for each_item in the_list:
		if isinstance(each_item,list):
			print_lol(each_item)
		else :
			print(each_item)