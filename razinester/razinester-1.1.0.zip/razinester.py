"""nester
i am a nester"""

def print_lol_test(the_list, level):
        for each_item in the_list:
                if isinstance(each_item, list):
                        print_lol_test(each_item, level+1)
                else:
                        for tab_stop in range(level):
                                print("    ", end="")
                        print(each_item)

