"""这是一个定义函数的模块，采用递归的方法查找列表中的所有项包括嵌套在数列中的数列各项"""
def fax(the_list):#函数可以调用本身，很神奇。。。
    for each_item in the_list:
        if isinstance(each_item,list):
            fax(each_item)#此处就是函数调用本身
        else:
            print(each_item)
"""movies=["the holy grail",1975,"terry jones & terry gilliam",91,
        ["graham chapman",
         ["michael palin","john cleese","terry gilliam","eric idle","terry jones"]]]
fax(movies)"""
