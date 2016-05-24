"""
Function that prints out every element of every list that is containted inside a list
"""




def print_lol(the_list,intend=False,tabs=0,):
    """recursively searches for list type items"""
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,intend,tabs + 1)
        else:
            if intend:
                for tab in range(tabs): 
                    print("\t", end='')

            print(each_item)
            
        
movies = [ "The Holy Grail", 1975, "terry Jones & terry Gilliam", 91,
           ["Graham Chapman",
            ["MIchael Palin", "John Cleese", "Terry Gilliam", "Eric Idle", "Terry Jones"]]]

names = ['John', 'Eric', ['Cleese', 'idle'], 'Michael', ['Palin']]
