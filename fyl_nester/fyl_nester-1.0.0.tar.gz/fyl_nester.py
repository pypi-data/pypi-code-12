"""Module nester:
	collect list operating functions that operat on list
"""

def print_lol(list_name):
	"""Function print_lol:
		print list which may include list in an iterative way.
	"""
	for each_element in list_name:
		if isinstance(each_element,list):
			print_lol(each_element)
		else:
			print(each_element)

#movies = ["The Holy Grail",1975,"Terry Jones & Terry Gilliam",91,
#		["Graham Chapman",["Michel Palin","John Cleese"]]]

#print_list_element(movies)

