def print_lol(the_list):
	for each_item in the_list:
		if isinstance(each_item,list):
			print_lol(each_item)
		else:
			print(str(each_item))



if __name__ == '__main__':
	ls1=[[1,7,8],2,3,4,[5,6]]
	print_lol(ls1)