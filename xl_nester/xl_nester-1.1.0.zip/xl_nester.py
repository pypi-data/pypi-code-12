def print_list(the_list,indent =False,level=0):
	for each in the_list:
		if isinstance(each,list):
			print_list(each,indent,level+1)
		else:
			if indent:
				for num in range(level):
					print("\t",end='')
			print(each)