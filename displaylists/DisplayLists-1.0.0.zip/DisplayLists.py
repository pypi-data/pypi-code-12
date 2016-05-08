"""This is to display the items of a list unwrapping each subsequent inner list"""

def display_list(list_name) :
    for item in list_name :
        if isinstance(item, list) :
            display_list(item)
        else :
            print(item)

            
