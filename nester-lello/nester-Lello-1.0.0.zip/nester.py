"""这是我的第一个模块"""
def print_lol(the_list):
    """本函数是打印刘表the_list内的所有内容，包括列表中的列表"""
    for each_list in the_list:
        if isinstance(each_list,list):
            print_lol(each_list)
        else:
            print(each_list)
