#!/usr/bin/python3
'''定义了print_lol函数，用print_lol（列表名）可以把列表中的每一个内容打印出来，包括嵌套的列表'''

def print_lol(the_list):
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item)
        else:
            print(each_item)


a=['1','2','3']
b=['4','5']
a.append(b)

print("a=",a)
print_lol(a)