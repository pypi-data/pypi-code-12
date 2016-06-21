def print_lol(the_list,level):
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,level)
        else:
            for tab_stop in range(level+1):
                print('\t',end='')
            print(each_item)
        
