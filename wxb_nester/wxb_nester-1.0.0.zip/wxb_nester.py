"""this is the standard way to include a multiple-line comment in your code."""

def print_lol(the_list):
       
        for pri in the_list:
                if isinstance(pri,list):
                        print_lol(pri)
                       
                else:
                        print(pri)
