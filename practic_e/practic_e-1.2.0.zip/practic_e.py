
"""
This code is use to iterate item in list and print them.
"""
def print_names(lst,indent=False,level=0):
    """
    Use recurise to finish finding all item in list
    :param lst:
    :return:
    """
    for item in lst:
        if isinstance(item,list):
            print_names(item,indent,level+1)
        else:
            if indent:
                for i in range(level):
                    print("\t",end='')
            print(item)


