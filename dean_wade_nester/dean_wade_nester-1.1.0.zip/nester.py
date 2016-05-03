def islist(the_list,level):
    """This function takes one positional arguments called "the_list",which
       is any Python list(of - possibly - nested lists). Each data item in
       the provided list is (recuraively) printed to the screen on it's own
       line."""


    for each_item in the_list:
        if isinstance(each_item, list):
            islist(each_item,level + 1)
        else:
            for tab_stop in range(level):
                print('\t',end = '')
            print(each_item)
