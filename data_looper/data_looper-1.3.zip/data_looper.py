def data_looper (list_name,indent=False,level=0):
	for each_one in list_name:
		if isinstance (each_one,list):
                                                        data_looper(each_one,indent,level+1)
		else:
			if indent:
                                                                print("\t"*level,end='')
			print(each_one)
