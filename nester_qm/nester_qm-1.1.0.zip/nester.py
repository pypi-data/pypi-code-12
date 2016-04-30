"""nester模块，提供了一个print_lol的函数，该函数作用是打印列表，包括列表中的列表"""

def print_lol(all_items, tab_cnt):
    """print_lol，需要输入一个列表，函数将其和内嵌列表进行打印"""
    for each_item in all_items:
        if isinstance(each_item, list):
            print_lol(each_item, tab_cnt+1)
        else:
            for cnt in range(tab_cnt):
                print("\t", end="")
            print(each_item)
