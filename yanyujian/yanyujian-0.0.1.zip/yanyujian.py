'''
Author:FengZiLi
Date:20160614 11:00
Description:HeadFirstPython 第一个发布包：递归多重列表
'''


def dumpList(lst):
    '''
    :param lst:一个集合或者单个对象
    :return: 无返回值，直接打印
    '''
    if isinstance(lst,list):
        for item in lst:
            dumpList(item)
    else:
        print(lst)