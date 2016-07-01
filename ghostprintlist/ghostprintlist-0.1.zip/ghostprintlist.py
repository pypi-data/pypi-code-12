"""This is the "listprint.py" module and it provide one function called listprint() which prints lists that may or may not include nested list."""

def listprint( mylist ):
    """
    This function takes one positional argument called "mylist", which is any Python list (of - possibly -nested lists).
    Each data item in the provided list is (recursively) printed to the screen on it's own line.
    """
    for each_item in mylist:
        if isinstance( each_item, list ):
            listprint( each_item )
        else:
            print( each_item )
            



"""
movies = [ "test1", "test2", "test3", [ 'test4', [ "test5", "test6" ] ] ]

if 0:
    print( movies )
print( len(movies) )

movies.extend( [ 'test4', "test5" ] )
print( movies )
movies.insert( 1, 1975 )
print( movies )
newarray = [ movies[0], 1975]
for item in newarray:
    print( item )

listprint( movies )
"""