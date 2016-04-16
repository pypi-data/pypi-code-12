"""This function takes a positional argument called "the_list", which
    is any Python list (of - possibly - nested lists). Each data item in the provided list is (recursively) printed to the screen on it's own line.
    A second argument for indentation and a third called “level" is used to insert tab-stops when a nested list is encountered."""
def print_nL(the_list,indent=False , level=0):

  for each_item in the_list:
    if isinstance(each_item, list):
      print_nL(each_item, indent , level+1)
    else:
        if indent :
            for tab_stop in range(level):
                print("\t", end='')
        print(each_item)

