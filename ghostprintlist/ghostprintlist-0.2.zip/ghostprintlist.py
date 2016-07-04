"""This is the "listprint.py" module and it provide one function called listprint() which prints lists that may or may not include nested list."""

def listprint( mylist, indent=False, level=0 ):
    """
    This function takes one positional argument called "mylist", which is any Python list (of - possibly -nested lists).
    Each data item in the provided list is (recursively) printed to the screen on it's own line.
    """
    for each_item in mylist:
        if isinstance( each_item, list ):
            listprint( each_item, indent, level+1 )
        else:
            if indent:
                for tab_stop in range( level ):
                    print( "\t", end='' )
            print( each_item )
            


