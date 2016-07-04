#print all item in list

def printList(the_list, level = 0):
    """print all item in the list"""
    for each in the_list:
        if isinstance(each, list):
            printList(each, level + 1)
        else:
            for num in range(level):
                print('\t', end = '')
            print(each)
