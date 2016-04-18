def print_lol(the_list, level=0):
    """
    :param the_list:
    :return:
    """
    for each_movie in the_list:
        if(isinstance(each_movie,list)):
            print_lol(each_movie,level+1)
        else:
            for tab_stop in range(level):
                print("\t",end='')
            print(each_movie)