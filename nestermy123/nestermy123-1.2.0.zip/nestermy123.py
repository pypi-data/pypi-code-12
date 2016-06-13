def print_lol(the_list,level=-1):
    for each in the_list:
        if isinstance(each,list):
            if level>=0:
                print_lol(each,level+1)
            else:
                print_lol(each,-1)
        else:
            print("\t" * level,end='')
            print(each)
