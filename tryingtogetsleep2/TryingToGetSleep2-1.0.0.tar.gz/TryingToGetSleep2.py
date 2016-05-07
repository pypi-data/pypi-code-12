def nester (a,indent=False,level=0,print_line=sys.stdout):
    for b in a:
        if isinstance(b,list):
            nester(b,indent,level+1,print_line)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t",end='',file=print_line)
            print(b,file=print_line)
