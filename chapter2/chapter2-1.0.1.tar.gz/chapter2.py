def print_recursive(input):
    if isinstance(input,list):
        for inner in input:
            print_recursive(inner)
    else:
        print(input)

def print_recursive(input, level=0):
	if isinstance(input,list):
		for inner in input:
			print_recursive(inner,level + 1)
	else:
		"""Print the tab base on level, number of tabs = level"""
		for tab_stop in range(level):
			print("\t", end='');
		print(input)
	    

