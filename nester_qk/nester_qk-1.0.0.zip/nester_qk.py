"""nester.py模块，提供一个名为print_lol()的函数，用于打印列表，并且可以将多重嵌套的类别打印出来"""

def print_lol(the_list):
    """该函数通过判断参数是否为列表，如果是就利用递归的方式全部打印出来"""
    
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item)
        else:
            print(each_item)