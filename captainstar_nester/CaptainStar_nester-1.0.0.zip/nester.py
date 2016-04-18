"""这是nester.py模块，提供了一个名为print_lol()的函数，这个函数的作用
是打印列表，嵌套列表同样可以打印"""
def print_lol(the_list):
    """这个函数可以将任何list进行打印，各占一行"""
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item)
        else:
            print(each_item)
