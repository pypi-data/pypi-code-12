#print all item in list

def printList(the_list, level):
    """print all item in the list"""
    for each in the_list:
        if isinstance(each, list):
            printList(each, level + 1)
        else:
            for num in range(level):
                print('\t', end = '')
            print(each)
