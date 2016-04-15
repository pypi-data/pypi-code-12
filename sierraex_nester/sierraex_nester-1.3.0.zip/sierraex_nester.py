"""comments"""

def print_lol(lst, indent=False, tabs=0):
    """comments bla bla"""
    for i in lst:
        if isinstance(i, list):
            print_lol(i, indent, tabs+1)
        else:
            if indent:
                for t in range(tabs):
                    print("\t", end='')
            print(i)
