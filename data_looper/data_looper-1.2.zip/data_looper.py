def data_looper (list_name,level=0):
	for each_one in list_name:
		if isinstance (each_one,list):
			data_looper(each_one,level+1)
		else:
			for num in range(level):
				print("\t",end='')
			print(each_one)
