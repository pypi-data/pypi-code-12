''' the nester module only contains one function
    print_lol() which is given a list to print'''
import sys

def print_lol(lst, indent=False, lvl=0, output=sys.stdout):
  ''' the print_lol() function prints a given list
  if the list contains nested lists it prints them as well
  this is accomplished using recursion
  '''
  for item in lst:
    if isinstance(item, list):
      print_lol(item, indent, lvl + 1, output)
    else:
      if indent:
        for tab_stops in range(lvl):
          print('\t', end='', file=output)
      print(item, file=output)
