def print_list(the_list):
    for each_nums in the_list:
        if isinstance(each_nums,list):
            print_list(each_nums)
        else:
            print(each_nums)
