''' the nester module only contains one function
    print_lol() which is given a list to print'''


def print_lol(lst, lvl=0):
  ''' the print_lol() function prints a given list
  if the list contains nested lists it prints them as well
  this is accomplished using recursion
  '''
  for item in lst:
    if isinstance(item, list):
      print_lol(item, lvl + 1)
    else:
      for tab_stops in range(lvl):
        print('\t', end='')
      print(item)
