"""nester.py模块，提供一个名为print_lol()的函数，用于打印列表，并且可以将多重嵌套的类别打印出来"""

def print_lol(the_list, level=0):
    """该函数有一个参数：the_list,通过判断参数是否为列表，如果是就利用递归的方式全部打印出来,
    第二个参数：level，用于在嵌套循环中插入制表符"""
    
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, level+1)
        else:
            for TAB in range(level):
                print("\t", end='')
            print(each_item)