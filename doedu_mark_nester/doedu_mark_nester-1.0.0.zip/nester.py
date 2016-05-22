"""这是一个用于测试Python打包流程的程序,里面包含了一个print_lol的函数.这个函数的作用就是打印嵌套的列表"""

def print_lol(the_list):
    """递归打印列表中的所有数据,可打印嵌套的列表"""
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item)
        else:
            print(each_item)
            
