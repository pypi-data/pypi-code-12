"""nester.py模块，提供一个名为print_lol()的函数，用于打印列表，并且可以将多重嵌套的类别采取缩进的方式打印出来"""
import sys

def print_lol(the_list, indent=False, level=0, fh=sys.stdout):
    """该函数有一个参数：the_list,通过判断参数是否为列表，如果是就利用递归的方式全部打印出来,
    第二个参数：indent，用于判断是否增加制表符，
    第三个参数：level，用于在嵌套循环中插入制表符，默认为0
    第四个参数：fh，用于调整输出的目标，默认为sys.stdout 输出到屏幕"""
    
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, indent, level + 1, fh)
        else:
            if indent:
                for TAB in range(level):
                    print("\t", end='', file = fh)
            print(each_item, file = fh)
