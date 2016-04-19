# -*- coding: utf-8 -*-
#字符串相关函数

def fill_id(id,length):
    '''自动填充id到指定的长度'''
    idLength = len(str(id))
    if idLength>length:
        return str(id)
    else:
        return '0'*(length-idLength) + str(id)