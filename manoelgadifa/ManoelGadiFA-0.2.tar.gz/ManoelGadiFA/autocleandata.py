# -*- coding: utf-8 -*-
"""
Created on Sun Jun 19 21:19:59 2016

@author: knnkv
"""

def autocleandata(data0):
    print('Define which column is index\n'
    'print the number of the column starting with 0\n'  )
    userinput3=input()
    data0= data0.set_index(data0.columns[userinput3])
    print('Next. What should I do with outliers? \n'
    'type 1 to remove rows \n'
    'type 2 to keep them \n')
    userinput1=int(input())
    if userinput1 ==1:
        data0=data0[(np.abs(stats.zscore(data0)) < 3).all(axis=1)]
    elif userinput1==2:
        data0=data0
   
        
    print('OK, got it. What should I do with missing values (NaN, etc.)? \n'
    'type 1 to remove rows \n'
    'type 2 to make them equal to average \n'
    'type 3 to make them equal to zero \n')
    userinput2=int(input())
    if userinput2==1:
        data0=data0[(np.abs(stats.zscore(data0)) < 3).all(axis=1)]
    elif userinput2==2:
        data0=data0.apply(lambda x: x.fillna(x.mean()),axis=0)
    elif userinput2==3:
        data0=data0.fillna(0)
    return(data0)