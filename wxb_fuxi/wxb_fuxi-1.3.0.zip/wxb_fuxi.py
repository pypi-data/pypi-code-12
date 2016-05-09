def print_lol(the_list，indent=false,level=0):
    for each_line in the_list:
        if isinstance(each_line,list):
            print_lol(each_line,indent,level+1)
        else:
            if indent:
                for each_t in range(level):
                    print("\t",end='')
            print(each_line)

    
    
