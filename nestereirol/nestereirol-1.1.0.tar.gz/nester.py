"""
Function that prints out every element of every list that is containted inside a list
"""




def print_lol(the_list,tabs):
    """recursively searches for list type items"""
    counter = tabs
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,tabs + 1)
        else:
            for tab in range(tabs): 
                print("\t", end='')

            print(each_item)
            
        
movies = [ "The Holy Grail", 1975, "terry Jones & terry Gilliam", 91,
           ["Graham Chapman",
            ["MIchael Palin", "John Cleese", "Terry Gilliam", "Eric Idle", "Terry Jones"]]]
