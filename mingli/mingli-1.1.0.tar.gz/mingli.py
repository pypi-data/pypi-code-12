def print_lol(the_list, level):
''' It is an example. '''
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_list, level+1)
        else:
            for tab_sop in range(level):
                print('\t', end='')
            print(each_list)
