"""This is the "nester_cww.py" module and it provides one function called print_lol() which prints lists that may not include nested lists."""

def print_lol(the_list,indent=False,level=0,fn=sys.stdout):
        """This function takes one positional argument called "The list",which provided list is (recursively) printed to the screen on it's own line."""
	
        for each_item in the_list:
                if isinstance(each_item,list):
                        print_lol(each_item,indent,level+1,fn)
                else:
                        if indent:
                                for tab_stop in range(level):
                                        print('\t',end='',file=fn)
                        print(each_item,file=fn)
