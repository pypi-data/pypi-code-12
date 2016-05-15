"""Example module from chapter 2, Head First Python.  The module allows
you to print nested lists, by use of recursion. It's named the nester.py
 module, which provides the print_lol() frunction to print nested lists."""

import sys

def print_lol(the_list, indent = False, level=0, fh=sys.stdout):
    """For each item, check if it's a list; if so, keeping calling myself
       until not a list, then print to standard fhput"""
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item, indent, level+1, fh)
        else:
            if indent != False:
                for tab_stop in range(level):
                    print("\t", end ='', file=fh)
            print(each_item, file=fh)

