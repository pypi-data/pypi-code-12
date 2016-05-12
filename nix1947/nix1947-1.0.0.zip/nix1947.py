"""This is the nester.py module which provides one function printList
This print the all the list item, including nested list one by one
"""

def printList(theList):
    """Function to print all the nested List
    """
    for eachItem in theList:
        if isinstance(eachItem, list):
            printList(eachItem)
        else:
            print(eachItem)

