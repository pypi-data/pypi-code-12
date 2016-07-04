#print all item in list

def printList(the_list, isTab = False, level = 0):
    """print all item in the list"""
    for each in the_list:
        if isinstance(each, list):
            printList(each, isTab, level + 1)
        else:
            if isTab:
                for num in range(level):
                    print('\t', end = '')
            print(each)
