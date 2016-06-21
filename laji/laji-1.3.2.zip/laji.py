def laji(the_list,indent=False, level=0):
    for each_item in the_list:
        if isinstance(each_item, list):
            laji(each_item,indent=indent, level=level+1)
        else:
        	if indent:
        		for tab_stop in range(level):
        			print("\t", end="")
        	print(each_item)