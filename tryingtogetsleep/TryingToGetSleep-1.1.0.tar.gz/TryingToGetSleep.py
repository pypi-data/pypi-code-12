def nester (a,level):
    for b in a:
        if isinstance(b,list):
            nester(b,level+1)
        else:
            for tab_stop in range(level):
                print("\t",end='')
            print(b)
'''This is the function for unlock the beasts in the cage'''
