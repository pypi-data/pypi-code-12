""" This functio is Reprint the list withiin list recursively"""

def reprint(printlist):
	for eachitem in printlist:
		if isinstance(eachitem,list):
			reprint(eachitem)
		else:
			print(eachitem)