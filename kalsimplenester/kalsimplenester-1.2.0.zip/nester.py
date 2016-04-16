"""This module prints out each item in
a list including nested lists."""

def print_lol(the_list, level=0):
        """The function print_lol takes in a
        list as an argument and prints out each 
        item in the list. It is a recursive function
        so it can even print out nested lists. It also
        takes in a second argument, level that works out
        the number of tab stops."""

        for each_item in the_list:
                if isinstance(each_item, list):
                        print_lol(each_item, level+1)
                else:
                        for tab_stop in range(level):
                                print("\t", end='')
                        print(each_item)

