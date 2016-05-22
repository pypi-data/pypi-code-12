"""这是一个用于测试Python打包流程的程序,里面包含了一个print_lol的函数.这个函数的作用就是打印嵌套的列表"""

def print_lol(the_list,level):
    """递归打印列表中的所有数据,可打印嵌套的列表,level表示间隔,新版本测试"""
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,level+1)
        else:
            for tab_stop in range(level):
                print("\t",end = '')
            print(each_item)
            
