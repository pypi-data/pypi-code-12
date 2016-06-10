import os

BLOCK = 512

def istext(f_path):
    data = open(f_path).read(BLOCK)
    if "\0" in data:
        return False
    else:
        return True