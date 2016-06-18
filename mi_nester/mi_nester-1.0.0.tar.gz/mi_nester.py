"""
This module is used to loop print out the content in list
"""
def print_lol(the_list):
	for each_item in the_list:
		if isinstance(each_item,list):
			print_lol(each_item);
		else:
			print(each_item);

