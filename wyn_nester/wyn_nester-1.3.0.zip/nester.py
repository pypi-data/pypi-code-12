movies =[
	"the holy grail",1975,"terry jones & terry gilliam",91,
	["graham chapman",
	 ["michael palin","john cleese","terry gilliam","eric idle","terry jones"]]]
def print_lol(the_list):
	for each_item in the_list:
		if isinstance(each_item,list):
			print_lol(each_item)
		else:
			print(each_item)


def print_lol(the_list,level):
        for each_item in the_list:
                if isinstance(each_item,list):
                        print_lol(each_item,level+1)
                else:
                        for tab_stop in range(level):
                                print("\t", end='')
                        print(each_item)


def print_lol(the_list,indent=False,level=0):
        for each_item in the_list:
                if isinstance(each_item,list):
                        print_lol(each_item,indent,level+1)
                else:
                        if indent:                                
                                for tab_stop in range(level):
                                        print("\t"*level, end='')
                        print(each_item)
