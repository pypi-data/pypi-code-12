"""comments"""

def print_lol(lst, tabs):
    """comments bla bla"""
    for i in lst:
        if isinstance(i, list):
            print_lol(i, tabs+1)
        else:
            for t in range(tabs):
                print("\t", end='')
            print(i)
