# -*-coding=utf8-*-
'''这是nester模块，提供了一个名为print_lol()的函数，
这个函数的作用是打印列表，其中有可能包含（也可能不包含）嵌套列表。'''
def print_lol(the_list,the_num=0):
    '''这个函数取一个位置参数，名为"the_list"，这可以使任何Python列表。'''
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,the_num+1)
        else:
            for num in range(the_num):
                print("\t",end='')
            print (each_item)
