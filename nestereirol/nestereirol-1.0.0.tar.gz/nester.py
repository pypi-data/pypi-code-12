"""
Function that prints out every element of every list that is containted inside a list
"""




def print_lol(the_list):
    """recursively searches for list type items"""
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item)
        else:
            print(each_item)


movies = [ "The Holy Grail", 1975, "terry Jones & terry Gilliam", 91,
           ["Graham Chapman",
            ["MIchael Palin", "John Cleese", "Terry Gilliam", "Eric Idle", "Terry Jones"]]]
