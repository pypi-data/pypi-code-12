"""这是"nester.py"模块，提供了一个名为print_lol()的函数，函数的作用
是打印列表，包括多层的嵌套列表"""
def print_lol(the_list,indent=False,level=0):
	for each_list in the_list:
		if isinstance(each_list,list):
			print_lol(each_list,indent,level+1)
		else:
                        if indent:
                                for tab_stop in range(level):
                                print("\t",end='')
                        print(each_list)
