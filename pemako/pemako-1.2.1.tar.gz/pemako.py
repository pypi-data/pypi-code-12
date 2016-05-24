# -*- coding: utf8 -*-
"""这是 nester.py 模块，提供了一个名为print_lol()的函数，这个函数
的作用是打印列表，可以处理嵌套列表"""

def print_lol(test_list,indent=False, level=0):
    """这个函数是一个位置参数，名为'test_list'，这可以是任何Python
    列表（也可以是包含嵌套的列表）。所指定的列表中的每个数据项会（
    递归地）输出到屏幕上，各数据项各占一行。"""
    for each_item in test_list:
        if isinstance(each_item, list):
            print_lol(each_item,indent, level+1)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t", end="")
            print(each_item)

if __name__ == '__main__':
    movies = ["The Holy Grail", 1975, "Terry Jones & Terry Gilliam", 91,
            ["Graham Chapman", ["Michael Palin", "John Cleese", 
                "Terry Gilliam", "Eric Idle", "Terry Jones"]]]

    print_lol(movies)
    print(20*'--')
    print_lol(movies, True)
    print(20*'--')
    print_lol(movies, True, 1)
