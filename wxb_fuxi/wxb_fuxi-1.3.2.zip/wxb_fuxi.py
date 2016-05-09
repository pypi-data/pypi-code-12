import sys
def print_lol(the_list,indent=False,level=0,fh=sys.stdout):
    for each_line in the_list:
        if isinstance(each_line,list):
            print_lol(each_line,indent,level+1,fh)
        else:
            if indent:
                for each_t in range(level):
                    print("\t",end='',file=fh)
            print(each_line,file=fh)

    
    
