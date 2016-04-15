"""这是“text.py模块，提供了一个函数，用来打印列表，嵌套列表” """
def print_lol(x,indent=False,level=0):
	for y in x:
		if isinstance(y,list):			
			print_lol(y,indent,level+1)
		else:
			if indent==True:
				for tab_stop in range(level):
					print("\t",end='')
			print(y)









	




