"""the programm that displays a list,
   or the list of the list, by invoke the same function."""


def print_lol(the_list, intent= False ,level=0, file_object = sys.stdout):
    for item in the_list:
        if(isinstance(item, list)):
           print_lol(item, intent ,level+1, file_object)
        else:
            if intent:
                for tab_stop in range(level):
                    print("\t", end='', file = file_object)
            print(item , file = file_object)

