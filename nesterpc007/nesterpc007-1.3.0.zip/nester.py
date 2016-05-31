"""this is "nester.py" modle and it 
"""
def print_lol(the_list,index==false,level=0):
	"""this function"""
	for each_item in the_list:
		if isinstance(each_item,list):
			print_lol(each_item,index,level+1)
		else:
		if index:
		for tab_stop in range(level)
		  orubt("\t",end='')
			print(each_item)