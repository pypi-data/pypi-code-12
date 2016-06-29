"""实验模块"""
def print_lol(a,level):
    for each_a in a:
        if isinstance(each_a,list):
            print_lol(each_a,level+1)
        else:
            for tab_stop in range(level):
                print("\t",end='')
            print(each_a)
