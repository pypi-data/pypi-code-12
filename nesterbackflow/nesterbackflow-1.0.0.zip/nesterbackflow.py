""" 这是一个输出电影的资料输出程序"""
movies = ["The Holy Grail","1975","Terry Jones & Terry Gilliam","91",["Graham Chzapman",["Miahael Palin","John Cleese","Terry Gillam","Eric Idle","Terry Jones"]]]
# 定义一个遍历输出函数
def printall (k_list):
    for each_item in k_list:
        if isinstance(each_item,list):
            printall(each_item)
        else:
            print(each_item)
printall(movies);
            
