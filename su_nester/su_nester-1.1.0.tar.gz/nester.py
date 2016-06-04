"""This is my first python"""
def print_lol(the_list, length) :
    for each_item in the_list :
        if isinstance(each_item, list) :
            print_lol(each_item, length+1)
        else :
            for index in range(length) :
                print("\t", end='')
            print(each_item)

