"""This is a comment"""
"""this is is a nested module"""

def bidhu ():
    for each_item in movies:
        if isinstance(each_item,list):
            for nested_item in each_item:
                if isinstance(nested_item,list):
                    for deeper_item in nested_item:
                        if isinstance(deeper_item,list):
                            for deepest_item in deeper_item:
                                print(deepest_item)

                        else:
                            print(deeper_item)

                else:
                    print(nested_item)

        else:
            print(each_item)


def print_lol(the_list,indent,indent,level=0):
    for each_item in the_list:
        if isinstance(each_ite,list):
            print_lol(each_item,indent,level+1)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t",end='')
                print (each_item)
