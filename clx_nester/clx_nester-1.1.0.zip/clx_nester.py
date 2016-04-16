"""This is the "clx_nester.py" module and it provides one function called print_lol()
   which prints lists that may or may not include nested lists"""
def print_lol(the_list,level):
    """This function takes one positional argument called "the_list",which
       is any python list (of possibly nested lists). Each data item in this
       provided list is printed to the screen on its own line."""
    
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,level+1)
        else:
            print(each_item)
