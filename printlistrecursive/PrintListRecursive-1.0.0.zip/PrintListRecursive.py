"""this is comment
    nester function"""

def printListRecursive(listA, indent = False, level = 0):
    for l in listA:
        if isinstance(l, list):
            printListRecursive(l, indent, level + 1)
        else:
            if indent:
                for i in range(level):
                    print('\t', end='')
            print (l)

   
