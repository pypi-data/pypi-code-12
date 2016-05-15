import sys
"""
This code is use to iterate item in list and print them.
"""
def print_names(lst,indent=False,level=0,fh=sys.stdout):
    """
    Use recurise to finish finding all item in list
    :param lst:
    :return:
    """
    for item in lst:
        if isinstance(item,list):
            print_names(item,indent,level+1,fh)
        else:
            if indent:
                for i in range(level):
                    print("\t",end='',file=fh)
            print(item,file=fh)


