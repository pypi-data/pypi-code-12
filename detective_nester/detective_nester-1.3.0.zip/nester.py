"""这一模块的作用是打印列表，其中可能包含嵌套列表"""
def print_lol(the_list,indent=false,level=0):
    """这一函数接受参数，可以是任何python列表，函数会将列表的每个数据项递归输出到屏幕，每个数据项占一行"""
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,indent,level+1)
        else:
            if indent:
                print("\t"*level,end='')
            print(each_item)
