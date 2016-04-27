"""This module is used for iterating through the list
and printing the values in the list. This module also
supports nested lists (list within the lists)"""
def print_lol(the_list, level):
    """Assuming the input is a list, Iterate over each item.
    Check if the item is a list, if it is a list then call
    the same function recursively. Else print the item"""
    for item in the_list:
        if isinstance(item, list):
            print_lol(item, level+1)
        else:
            for tab_stop in range(level):
                print("\t",end="")
            print(item)
