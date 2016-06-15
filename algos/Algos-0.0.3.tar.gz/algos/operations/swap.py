"""
    This is the operations module that has all the basic operations specified that will be used frquently in programming
"""

class Swap(object):
    """
	Takes two values and swaps them 
        Basic Usage:
        
	    >>> instance = Swap(1,2)
        >>> value2, value1 = instance.get_swap_values()
        >>> print value1, value2
        2 1
    """
    def __init__(self, value1, value2):
        self.value1 = value1
        self.value2 = value2

    def get_swap_values(self):
        return self.value2, self.value1