
movies=[
	"The Holy Grail",1975,"Terry Jones & Terry Gilliam",91,
	  ["Graham Chapman",
	   ["Michael Palin","John Cleese","Terry Gilliam","Eric Idle","Terry Jones"]]]
"""This id the"nester.py"module and it provodes one function called print_lol() while prints lists that may not include nested lists."""
def print_lol(the_list,indent=False,level=0):
   """This function takes one pstitional argument called "the list",whitch is any python list(of-possibly-nested lists).Sach data item in the provided list is (recursively)printed to the screen on it'own line"""
   for each_item in the_list:
      if isinstance(each_item,list):
         print_lol(each_item,indent,level+1)
      else:
         if indent:
            for tab_stop in range(level):
               print("\t",level,end='')
         print(each_item)






