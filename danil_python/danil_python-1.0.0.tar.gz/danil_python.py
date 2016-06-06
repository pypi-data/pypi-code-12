"""this is danil python study file"""

def print_lol(the_list):
#hello, this is parameter def
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item)
        else:
            print(each_item)


