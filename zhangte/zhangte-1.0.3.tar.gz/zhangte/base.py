#coding:utf8
import re

class Base():
    #去除掉所有的html标签
    def cuthtml(self,content,P=0):
        if P == 0:
            p2 = re.compile(r'</?\w+[^>]*>|</?(a|p style|blockquote)[^>]*>|(http.+?html)|&.*?;')
        else:
            p2 = re.compile(r'</?[^(/?p|br)]\w+[^>]*>|</?(a|p style|blockquote)[^>]*>|(http.+?html)|&.*?;')  #包含p,br等标签
        return p2.sub('',content) #去除所有的html代码

