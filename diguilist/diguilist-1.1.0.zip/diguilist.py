def myadd(cast, level):
    for n in cast:
        if isinstance(n, list):
            myadd(n, level+1)
        else:
            for tab_stop in range(level):
                print("\t", end='')
            print(n)










