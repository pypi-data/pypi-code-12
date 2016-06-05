"""This is the “nester.py" module, and it provides one function called
print_lol() which prints lists that may or may not include nested lists"""

"""This function takes a positional argument called “the_list", which is any
Python list (of, possibly, nested lists). Each data item in the provided list
is (recursively) printed to the screen on its own line"""
def print_lol(the_list,count):
	print("list ",count)
	for each_item in the_list:
		if(isinstance(each_item,list)):
			count = count+1
			print_lol(each_item,count)
		else:
			print(each_item)
