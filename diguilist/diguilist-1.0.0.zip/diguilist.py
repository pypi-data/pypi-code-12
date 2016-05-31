def myadd(item):
    for n in item:
        print("n=",n)
        if isinstance(n,list):
            myadd(n)
        else:
            print(n)










