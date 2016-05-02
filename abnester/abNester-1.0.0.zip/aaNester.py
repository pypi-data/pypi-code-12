"""This module consists of a function printRecursiveList which prints all the contents line by line in a list"""



def printRecursiveList(aList):
	"""This function accepts a list as an argument and print the contents of list one by one"""
	if(not isinstance(aList,list)):
		print(aList)
	else:
		for eachItem in aList:
			printRecursiveList(eachItem)
