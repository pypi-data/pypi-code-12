"""这是“nesterv.py”模块，提供了"""
import sys
def print_lol(the_list,indent=False,level=0,fh=sys.stdout):
    """这个函数去一个位置函数，名为“the_list”"""

    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,indent,level+1,fh)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t",end="",file=fh) 
            print(each_item,file=fh)
