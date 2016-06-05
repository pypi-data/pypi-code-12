'''this is a 'neste.py' modeule and it provider one function called print_lol()
   which prints lists that may or may not include neated lists'''
def print_lol(the_list):
    '''this function takes one positional argument called "the_list";which is any
        list Python list(of -possibly -neated lists).Each data item in the provided
        list is ( recursively) printed to the screen on it's own line .'''
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item)
        else:
            print(each_item)
