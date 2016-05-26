#这是我的第一个python模块代码，函数实现列表的打印输出功能
def print_lol(the_list):
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item)
        else:
            print(each_item)
