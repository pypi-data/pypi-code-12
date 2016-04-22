"""This is nester py modules, provide a function, Print_lol by name."""
"""This function print out all items that are included in List if Nested list 
exist """
import sys
def print_lol(the_list, indent=False, level=0,fh=sys.stdout):
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item, indent, level+1,fh) #recursively!
		else:
			if indent:
				for tab_stop in range(level):
					print("\t", end='',file=fh)
			print(each_item,file=fh)
