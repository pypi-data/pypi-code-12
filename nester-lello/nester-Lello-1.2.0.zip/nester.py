"""这是我的第一个模块"""
def print_lol(the_list,level=0):
    """本函数是打印刘表the_list内的所有内容，包括列表中的列表"""
    for each_list in the_list:
        if isinstance(each_list,list):
            print_lol(each_list,level+1)
        else:
            for tab_stop in range(level):
                print('\t',end='')
            print(each_list)
