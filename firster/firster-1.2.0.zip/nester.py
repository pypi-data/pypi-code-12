"""这是“nester.py”模块，提供了一个名为print_lol()的函数，
这个函数的作用是打印列表，其中有可能包含也有可能不包含嵌套列表"""
def print_lol(the_list,level=0):
	"""这个函数取一个位置参数the_list，
	他可以是任何列表，该列表中的每个数据都会递归地打印到屏幕上，
	各数据项各占一行。第二个参数用来在遇到嵌套列表时插入制表符"""
	for each_item in the_list:
		if isinstance(each_item,list):
			print_lol(each_item,level+1)
		else:
			for tab_stop in range(level):
				print("\t",end='')
			print(each_item)
