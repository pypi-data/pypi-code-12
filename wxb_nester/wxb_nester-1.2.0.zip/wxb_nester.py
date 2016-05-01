"""this is the standard way to include a multiple-line comment in your code."""

def print_lol(the_list,level=0):
       
        for pri in the_list:
                if isinstance(pri,list):
                        print_lol(pri,level+1)
                       
                else:
                        for prij in range(level):
                          print("\t",end='')
                        print(pri)
