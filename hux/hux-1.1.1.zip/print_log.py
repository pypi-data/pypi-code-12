__author__ = 'hx'
#codeing =utf_8
'''
这是第一个python模块，包含了产用的print函数调用，并编写了一个嵌套调用的打印list的函数
'''
#定义一个嵌套处理函数，打印list清单的函数 print_log(movies)
def print_list(the_list,level=0):
    for each_item in the_list:
        if(isinstance(each_item,list)):
            print_list(each_item,level+1)
        else:
            for tab_stop in range(level):
                print("\t",end='')
            print(each_item)
#函数end
