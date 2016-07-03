#print all item in list
def printList(the_list):
    """print all item in the list"""
    for each in the_list:
        if isinstance(each, list):
            printList(each)
        else:
            print(each)
