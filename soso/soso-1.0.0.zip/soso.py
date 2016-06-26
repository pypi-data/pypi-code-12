"""实验模块"""
def print_lol(a):
    for each_a in a:
        if isinstance(each_a,list):
            print_lol(each_a)
        else:
            print(each_a)
