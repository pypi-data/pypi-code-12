"""这一模块的作用是打印列表，其中可能包含嵌套列表"""
def print_lol(the_list,level):
    """这一函数接受参数，可以是任何python列表，函数会将列表的每个数据项递归输出到屏幕，每个数据项占一行"""
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,level+1)
        else:
            for tab_stop in range(level):
                print("\t",end='')
            print(each_item)
