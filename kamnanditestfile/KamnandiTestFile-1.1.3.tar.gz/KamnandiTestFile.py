"""This is the standard way to include comment in your code"""

def print_lol(the_list,indent=false,level=0):
	"""this is to process list within a list"""
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item,true,level+1)
		else:
                        for tab_stop in range(level):
                                print("\t",end='')
                        print(each_item, false)

