'''This is the nester.py module abd it provides one function called print_lol() which prints lists
   that may ot may not include nested lists'''
   
def print_lol(the_list):

	'''This function takes one argument called 'the_list' which is any python list. Each data item in
	   the provided list is recusively printed to the screen on its own line'''
	   

	for each_item in the_list:
		if isinstance(each_item,list):
			print_lol(each_item)
		else:
			print(each_item)


'''Example:
        array=[1,2,3,[4,5,6,7,[1,2,3,4,[6,7,8,9,],5,6],8,9,10],4,5,6]

'''	