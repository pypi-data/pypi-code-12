"""
    This is the operations.py module that has all the basic operations specified that will be used frquently in programming
"""

class Swap(object):
    """
	Takes two values and swaps them 
        Basic Usage:
        
	swap_obj = Swap(1,2)
        value2, value1 = swap_obj.get_swap_values()
    """
    def __init__(self, value1, value2):
        self.value1 = value1
        self.value2 = value2

    def get_swap_values(self):
        return self.value2, self.value1


