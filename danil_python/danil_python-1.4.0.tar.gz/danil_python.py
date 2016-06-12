"""this is danil python study file"""

def print_lol(the_list, indent=False, level=0, fo=sys.stdout):
#hello, this is parameter def
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, indent, level+1, fo)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t", end='', file=fo)
            print(each_item, file=fo)


