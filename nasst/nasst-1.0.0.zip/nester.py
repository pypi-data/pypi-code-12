"""This function is for calculate"""
def print_lol(the_list):
    """contains one for and if else"""
    for mx in the_list:
        if isinstance(mx, list):
            print_lol(mx)
        else: print(mx)


