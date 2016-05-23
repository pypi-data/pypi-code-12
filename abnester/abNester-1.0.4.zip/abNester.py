"""This module consists of a function printRecursiveList which prints all the contents line by line in a list"""



def printRecursiveList(aList,indent =False,level=0):
	"""This function accepts a list as an argument and print the contents of list one by one"""
	if(not isinstance(aList,list)):
		if indent:
			for l in range(level):
				print("\t ",end='')
		print(aList)
	else:
		for eachItem in aList:
			printRecursiveList(eachItem,indent,level+1)



