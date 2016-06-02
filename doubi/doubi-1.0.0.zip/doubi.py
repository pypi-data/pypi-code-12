# coding=utf-8
'''
Created on 2016年6月1日

@author: cs
'''
movies=["jianbingxia","2016","dapeng","150",
        ["dapeng",
         ["cuizhijia","xiaoshenyang","zengzhiwei"]]]
print(movies[4][1][1])
def doubi(y): 
    for x in y:
        if isinstance(x,list):
            doubi(x)
        else:
            print(x)
doubi(movies)