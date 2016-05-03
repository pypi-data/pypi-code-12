def nester (a):
    for b in a:
        if isinstance(b,list):
            nester(b)
        else:
            print(b)
'''This is the function for unlock the beasts in the cage'''
