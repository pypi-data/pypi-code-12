'''这是‘nesterdf’模块，提供了一个名为print_lol()的函数，这个函数用于打印列表，其中可能包含嵌套列表。'''
def print_lol(the_list):
    '''这个函数取一个位置函数，名为"the_list"，这可以是任何Python列表。所指定的列表中的所所有数据会（递归的）输出到屏幕上，各数据各占一行。'''
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item)
        else:
            print(each_item)
            
zai_ru_cheng_gong=['载入成功']
print_lol(zai_ru_cheng_gong)
