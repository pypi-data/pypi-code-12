def print_lol(the_list,dent=False,level=0):
       for each_item in the_list:
                 if isinstance(each_item,list):
                            print_lol(each_item,dent,level+1)
                 else:
                     if dent:
                         for tab_stop in range(level):
                             print("\t",end="")
                print(each_item)











                       
