"""This function helps to display all single elements of a lists, even and especially if the list contains nested lists,
which may include even more nested lits and so on. Values from different lists are also indented, to make distinction clear."""

def print_lol(the_list, indent = False, level=0):
        for each_item in the_list:
                if isinstance(each_item, list):
                        print_lol(each_item, indent, level+1)
                else:
                        if indent:
                                for tab_stop in range(level):
                                        print("\t", end="")
                        print(each_item)


"""Syntax: print_lol(x),
x = list

Displays all single elements of included in your lists and all lists within"""
