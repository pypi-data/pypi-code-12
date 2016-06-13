import sys
def print_lol(the_list,level=-1,def_f=sys.stdout):
    for each in the_list:
        if isinstance(each,list):
            if level>=0:
                print_lol(each,level+1,def_f)
            else:
                print_lol(each,-1,def_f)
        else:
            print("\t" * level,end='',file=def_f)
            print(each,file=def_f)
