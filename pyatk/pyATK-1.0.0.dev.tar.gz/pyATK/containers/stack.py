# -*- coding: utf-8 -*-


###
# Stack container based on a list for its internal storage
#
class Stack:
    def __init__(self):
        self.internal_list = list()

    def is_empty(self):
        """
        >>> s.is_empty()
        True
        """
        return len(self.internal_list) == 0

    def pop(self):
        """
        >>> s.pop()
        """
        return self.internal_list.pop() if self.internal_list else None

    def push(self, element):
        """
        >>> s.push(1)
        >>> s.push(2)
        """
        self.internal_list.append(element)

    def top(self):
        """
        >>> s.top()
        2
        """
        return self.internal_list[-1]

    def __print_content(self):
        print("+---------+")
        for i in range(len(self.internal_list)):
            print("   " + str(self.internal_list[len(self.internal_list) - 1 - i]))
            print("+---------+")

    def size(self):
        """
        >>> s.size()
        2
        """
        return len(self.internal_list)
        
        
if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False, extraglobs={'s': Stack()})