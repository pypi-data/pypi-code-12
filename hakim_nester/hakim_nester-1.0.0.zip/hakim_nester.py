"""Example module from chapter 2, Head First Python.  The module allows
you to print nested lists, by use of recursion. It's named the nester.py
 module, which provides the print_lol() frunction to print nested lists."""


def print_lol(the_list):
    """For each item, check if it's a list; if so, keeping calling myself
       until not a list, then print to standard output"""
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item)
        else:
            print(each_item)
