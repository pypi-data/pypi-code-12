"""This is the nester.py module and it provides one function called
printed print_lol() which prints lists that may or
may not include nested lists."""

def print_lol(the_list, level):
     """This function takes a positional argument called "the list",
which is any Python list (of - possibly - nester lists). Each data item in
the provide list is (recursively) ptinted to the screen on it`s own line.
A second argument call "level" is used to insert tab-stop which a nested list
is encountered."""
     
     for each_item in the_list:
         if isinstance(each_item,list):
             print_lol(each_item,level+1)
         else:
              for tab_stop in range(level):
                   print("\t", end='')
              print(each_item)
