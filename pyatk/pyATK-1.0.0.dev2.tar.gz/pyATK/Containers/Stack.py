# -*- coding: utf-8 -*-


###
# Stack container based on a list for its internal storage
#
class Stack:
    """
    >>> s = Stack()
    >>> s.isEmpty()
    True
    >>> s.push(1)
    >>> s.push(2)
    >>> s.top()
    2
    >>> s.size()
    2
    >>> s.pop()
    2
    >>> s.top()
    1
    >>> s.size()
    1
    """
    def __init__(self):
        self.internal_list = list()

    def isEmpty(self):
        return len(self.internal_list) == 0

    def pop(self):
        return self.internal_list.pop() if self.internal_list else None

    def push(self, element):
        self.internal_list.append(element)

    def top(self):
        return self.internal_list[-1]

    def size(self):
        return len(self.internal_list)

