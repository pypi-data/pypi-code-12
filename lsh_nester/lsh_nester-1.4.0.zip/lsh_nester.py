'''def print_all_list(the_list,level=0):
    for item in the_list:
        if isinstance(item,list) == False:
            for tab_stop in range(level):
                    print("\t",end='')
            print(item)
        else:
            print_all_list(item,level+1)'''

def print_all_list(the_list,indent=False,level=0):
    for item in the_list:
        if isinstance(item,list) == False:
            if indent:
                for tab_stop in range(level):
                    print("\t",end='')
            print(item)
        else:
            print_all_list(item,indent,level+1)
