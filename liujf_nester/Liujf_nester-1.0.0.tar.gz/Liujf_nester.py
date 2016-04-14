def print_lol(the_lists,the_level):
    for each_item in the_list:
    	if isinstance(each_item,list):
    		print_lol(each_item)
    	else:
    		for tab_stop in range(the_level):
    			print("\t",end='')
    		print(each_item)