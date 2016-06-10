"""这是“nesterv.py”模块，提供了"""

def print_lol(the_list,indent=False,level=0):
    """这个函数去一个位置函数，名为“the_list”"""

    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,indent,level+1)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t",end="") 
            print(each_item)
