"""This is the "nester.py" module and it provides one function called print_lol()
which prints lists that may or may not include nested lists."""

from __future__ import print_function

def print_lol(the_list, indent=False, level=0):
    """ A function that uses recursion to print lists within lists within lists"""
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, indent, level + 1)
        else:
            if indent:
                for tabStop in range(level):
                    print("\t", end='')
            print(each_item)

movies = ["The Holy Grail", 1975, "Terry Jones & Terry Gilliam", 91,
["Graham Chapman", ["Michael Palin", "John Cleese",
"Terry Gilliam", "Eric Idle", "Terry Jones"]]]

print_lol(movies, True, 0)

