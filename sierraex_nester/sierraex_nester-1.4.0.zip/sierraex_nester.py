"""comments"""
import sys

def print_lol(lst, indent=False, tabs=0, fh=sys.stdout):
    """comments bla bla"""
    for i in lst:
        if isinstance(i, list):
            print_lol(i, indent, tabs+1, fh)
        else:
            if indent:
                print("\t" * tabs, end='', file=fh)
            print(i, file=fh)
