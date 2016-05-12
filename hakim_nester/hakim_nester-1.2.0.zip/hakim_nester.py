"""Example module from chapter 2, Head First Python.  The module allows
you to print nested lists, by use of recursion. It's named the nester.py
 module, which provides the print_lol() frunction to print nested lists."""


def print_lol(the_list, level=0):
    """For each item, check if it's a list; if so, keeping calling myself
       until not a list, then print to standard output"""
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item, level+1)
        else:
            for tab_stop in range(level):
                print("\t", end ='')
            print(each_item)
