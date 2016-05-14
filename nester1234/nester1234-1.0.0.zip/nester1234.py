"""Head First Python
	My First Python Module """
def print_lol(the_list):
	for each_item in the_list:
	#for every each_item
		if isinstance(each_item, list):
		#Recursive func call
			print_lol(each_item)
		else:
			print(each_item)