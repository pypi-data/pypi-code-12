"""函数模块，输入列表（含嵌套列表），可以将列表中的元素依次输出"""
def print_list(the_list):
    for each_line in the_list:
        if isinstance(each_line,list):
            print_list(each_line)
        else:
            print(each_line)
