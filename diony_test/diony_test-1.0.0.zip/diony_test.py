def print_lol(the_list,tab_index=False,level=0):
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,tab_index,level+1)
        else:
            if tab_index == True:
                for i in range(level):
                    print("\t",end='')
            print(each_item)
