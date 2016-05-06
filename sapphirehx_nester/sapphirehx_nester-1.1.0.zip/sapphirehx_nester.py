def print_lol(the_list,level):
    for letters in  the_list:
        if isinstance(letters,list):
            print_lol(letters,level+1)
        else:
            for tab_stop in range(level):
                print('\t',end='')
            print(letters)
            