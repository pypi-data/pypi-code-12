"""
    This is the sorting module that has all the basic operations specified that will be used frquently in programming
"""

class InsertionSort(object):
    """
	Takes two values and swaps them
        Basic Usage:

        Simply Sorting

	    >>> instance = InsertionSort([12, 65, 23, 67, 45, 78, 90, 34, 23, 67, 45])
        >>> sorted_list = instance.sort()
        [12, 23, 23, 34, 45, 45, 65, 67, 67, 78, 90]

        Sorting in the Reverse Order

        >>> instance = InsertionSort([12, 65, 23, 67, 45, 78, 90, 34, 23, 67, 45])
        >>> sorted_list = instance.sort(reverse=True)
        [90, 78, 67, 67, 65, 45, 45, 34, 23, 23, 12]
    """
    def __init__(self, *args):
        self.input_list = args[0]

    def sort(self, reverse=False):
        for i in range(1, len(self.input_list)):
            key = self.input_list[i]
            j = i - 1
            if reverse==False:
                while j>=0 and self.input_list[j]>key:
                    self.input_list[j+1] = self.input_list[j]
                    j -= 1
                self.input_list[j+1] = key
            elif reverse == True:
                while j>=0 and self.input_list[j]<key:

                    self.input_list[j+1] = self.input_list[j]
                    j -= 1
                self.input_list[j+1] = key
        return self.input_list