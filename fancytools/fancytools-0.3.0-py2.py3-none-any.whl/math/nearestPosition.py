# -*- coding: utf-8 -*-

def nearestPosition(array, value):
	'''
	return the index of that value that is most similar in the array
	needs a numpy.1darray
	
	>>> import numpy
	>>> a = numpy.array([1,2,3,7,3,647,223,777])
	>>> nearestPosition(a, 22)
	3
	>>> nearestPosition(a, 300)
	6
	'''
	difference_list = abs(array - value)
	return difference_list.argmin()



if __name__ == "__main__":
	import doctest
	doctest.testmod()