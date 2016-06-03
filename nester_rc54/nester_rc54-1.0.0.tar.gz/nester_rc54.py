"""
This is the nester module.  It provides one function called print_lol()
which prints lists that may or may not include nested lists."""

def print_lol(the_list):
    """ This function takes a positional aruguemt called "the_list", which is any Python list, and may contain nested lists, and recursively printes each 
    item to the screen on its own line.
    """
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item)
        else:
            print(each_item)
