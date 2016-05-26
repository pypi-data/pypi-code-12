#这是我的第一个python模块代码，函数实现列表的打印输出功能
def print_lol(the_list,indent=False,level=0):
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,indent,level+1)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t",end=' ')
            print(each_item)
