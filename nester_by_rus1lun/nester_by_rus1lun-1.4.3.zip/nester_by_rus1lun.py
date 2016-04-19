"""the programm that displays a list,
   or the list of the list, by invoke the same function."""

import sys

def print_lol(the_list, intent= False ,level=0, fh_id = sys.stdout):
    for item in the_list:
        if(isinstance(item, list)):
           print_lol(item, intent ,level+1, fh_id)
        else:
            if intent:
                for tab_stop in range(level):
                    print("\t", end='', file = fh_id)
            print(item , file = fh_id)

