"""This is the "nester.py"module.It provides one funtion called print_lof()，which prints lists that may or may not include nested list"""

def print_lof(the_list,indent=False,level=0):
        """ The function takes one positional argument called the_list,which is any pythonlist (of-possibly-nested lists).
        Each data item in the provided list is (recursively) printed to the screen on its own line.The argument of indent expresses using TAB or not.The argument called level is the number of asserting the TAB when occurring nested list.
        """

        for each_item in the_list:
                if(isinstance(each_item,list)):
                        print_lof(each_item,indent,level+1)
                else:
                        if(indent==True):
                                for tab_stop in range(level):
                                        print("\t",end='')
                        print(each_item)
